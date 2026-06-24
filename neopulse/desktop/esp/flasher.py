"""ESP32 firmware flashing module for NeoPulse Studio."""

import os
import subprocess

import serial
import serial.tools.list_ports


class ESPFlasher:
    """Handles MicroPython firmware flashing and ESP32 port detection."""

    # Official MicroPython firmware URLs for ESP32-S3
    FIRMWARE_URLS = {
        "esp32s3": "https://micropython.org/resources/firmware/ESP32_S3_GENERIC-20240221-v1.23.0.bin",
        "esp32": "https://micropython.org/resources/firmware/ESP32_GENERIC-20240221-v1.23.0.bin",
        "esp32c3": "https://micropython.org/resources/firmware/ESP32_C3_GENERIC-20240221-v1.23.0.bin",
    }

    # esptool.py chip types
    CHIP_TYPES = {
        "esp32s3": "esp32s3",
        "esp32": "esp32",
        "esp32c3": "esp32c3",
    }

    def __init__(self):
        self._esptool_available = self._check_esptool()

    def _check_esptool(self) -> bool:
        """Check if esptool.py is installed."""
        try:
            result = subprocess.run(["esptool.py", "--version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def install_instruction(self) -> str:
        """Return installation instructions for esptool."""
        return (
            "esptool.py ist nicht installiert.\n\n"
            "Installation:\n"
            "  pip install esptool\n\n"
            "Oder für systemweite Installation:\n"
            "  sudo apt install python3-esptool\n"
        )

    def get_available_firmwares(self) -> list:
        """Return list of available MicroPython firmwares."""
        return [
            {
                "name": "ESP32-S3 GENERIC (v1.23.0)",
                "url": self.FIRMWARE_URLS["esp32s3"],
                "chip": "esp32s3",
                "size": "~2MB",
            },
            {
                "name": "ESP32 GENERIC (v1.23.0)",
                "url": self.FIRMWARE_URLS["esp32"],
                "chip": "esp32",
                "size": "~2MB",
            },
            {
                "name": "ESP32-C3 GENERIC (v1.23.0)",
                "url": self.FIRMWARE_URLS["esp32c3"],
                "chip": "esp32c3",
                "size": "~800KB",
            },
        ]

    def detect_ports(self) -> list:
        """Detect available ESP32 serial ports."""
        ports = []
        try:
            all_ports = serial.tools.list_ports.comports()
            for port in all_ports:
                # Check if it might be an ESP32
                desc = port.description.lower()
                hwid = port.hwid.lower()

                is_esp32 = (
                    "esp32" in desc
                    or "esp32-s3" in desc
                    or "usb-jtag" in hwid
                    or "cp2102" in hwid
                    or "ch9102f" in hwid
                    or "ft232" in hwid
                    or "usbserial" in hwid
                )

                if is_esp32 or "esp" in hwid:
                    ports.append(
                        {
                            "port": port.device,
                            "description": port.description,
                            "hwid": port.hwid,
                        }
                    )
                elif not ports:  # Fallback: show all serial ports
                    ports.append(
                        {
                            "port": port.device,
                            "description": port.description or port.device,
                            "hwid": port.hwid,
                        }
                    )
        except Exception as e:
            print(f"Port detection error: {e}")

        return ports

    def flash_firmware(
        self, port: str, firmware_url: str = None, firmware_path: str = None, chip: str = "esp32s3"
    ) -> dict:
        """Flash MicroPython firmware to ESP32.

        Returns: {'success': bool, 'message': str}
        """
        if not self._esptool_available:
            return {"success": False, "message": self.install_instruction()}

        # First erase flash
        try:
            print(f"Erasing flash on {port}...")
            result = subprocess.run(
                ["esptool.py", "--port", port, "erase_flash"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return {"success": False, "message": f"Erase failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Erase timed out. Try pressing BOOT button on ESP32.",
            }

        # Download firmware if URL provided
        fw_path = firmware_path
        if firmware_url and not firmware_path:
            import tempfile
            import urllib.request

            with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
                fw_path = f.name
                print(f"Downloading firmware to {fw_path}...")
                try:
                    urllib.request.urlretrieve(firmware_url, fw_path)
                except Exception as e:
                    os.unlink(fw_path)
                    return {"success": False, "message": f"Download failed: {e}"}

        if not fw_path or not os.path.exists(fw_path):
            return {"success": False, "message": "Firmware file not found."}

        # Flash firmware
        try:
            print(f"Flashing firmware to {port}...")
            result = subprocess.run(
                [
                    "esptool.py",
                    "--port",
                    port,
                    "--baud",
                    "460800",
                    "write_flash",
                    "-z",
                    "0x1000",
                    fw_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return {"success": True, "message": "Firmware flashed successfully!"}
            else:
                return {"success": False, "message": f"Flash failed: {result.stderr}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Flash timed out. Check connection and try again."}
        finally:
            # Clean up temp file
            if firmware_url and fw_path and os.path.exists(fw_path):
                try:
                    os.unlink(fw_path)
                except:
                    pass

    def enter_bootloader(self, port: str) -> dict:
        """Put ESP32 into bootloader mode via DTR/RTS."""
        try:
            with serial.Serial(port, 115200, timeout=1) as ser:
                ser.setDTR(False)
                ser.setRTS(True)
                import time

                time.sleep(0.1)
                ser.setDTR(True)
                ser.setRTS(False)
                time.sleep(0.1)
            return {"success": True, "message": "Entered bootloader mode."}
        except Exception as e:
            return {"success": False, "message": f"Error: {e}"}

    def get_chip_info(self, port: str) -> dict:
        """Get chip information from ESP32."""
        if not self._esptool_available:
            return {"success": False, "message": "esptool.py not installed."}

        try:
            result = subprocess.run(
                ["esptool.py", "--port", port, "chip_id"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Timeout. Check connection."}

    def verify_installation(self, port: str) -> dict:
        """Verify MicroPython is running on the ESP32."""
        try:
            with serial.Serial(port, 115200, timeout=2) as ser:
                # Send a simple command
                ser.write(b'print("hello")\n')
                import time

                time.sleep(0.5)
                output = ser.read(100).decode("utf-8", errors="replace")

                if "hello" in output.lower():
                    return {"success": True, "message": "MicroPython is running!"}
                else:
                    return {"success": False, "message": f"Unexpected output: {output}"}
        except Exception as e:
            return {"success": False, "message": f"Verification error: {e}"}

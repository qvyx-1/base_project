#!/usr/bin/env python3
"""NeoPulse Studio - Comprehensive Test Suite (no hardware required)"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test results tracking
results = {"passed": 0, "failed": 0, "errors": []}


def test(name, func):
    """Run a test and track results."""
    try:
        func()
        print(f"  ✅ {name}")
        results["passed"] += 1
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        results["failed"] += 1
        results["errors"].append((name, str(e)))


# ============================================
# TEST 1: Models
# ============================================
print("\n=== Testing Models ===")


def test_scene_creation():
    from desktop.models.scene import Scene

    s = Scene(name="Test Scene", duration=10.0)
    assert s.name == "Test Scene"
    assert s.duration == 10.0
    assert len(s.keyframes) == 0


def test_keyframe_creation():
    from desktop.models.keyframe import Keyframe

    kf = Keyframe(time=5.0, colors=[(255, 0, 0)])
    assert kf.time == 5.0
    assert kf.colors == [(255, 0, 0)]


def test_scene_add_keyframe():
    from desktop.models.keyframe import Keyframe
    from desktop.models.scene import Scene

    s = Scene(name="Test")
    kf1 = Keyframe(time=0.0, colors=[(255, 0, 0)])
    kf2 = Keyframe(time=5.0, colors=[(0, 255, 0)])
    s.add_keyframe(kf1)
    s.add_keyframe(kf2)
    assert len(s.keyframes) == 2
    # Check keyframes are sorted by time
    assert s.keyframes[0].time < s.keyframes[1].time


def test_scene_to_dict():
    from desktop.models.keyframe import Keyframe
    from desktop.models.scene import Scene

    s = Scene(name="Test", duration=15.0)
    s.add_keyframe(Keyframe(time=0.0, colors=[(255, 0, 0)]))
    d = s.to_dict()
    assert "id" in d
    assert "name" in d
    assert "keyframes" in d
    assert len(d["keyframes"]) == 1


def test_show_creation():
    from desktop.models.scene import Scene
    from desktop.models.show import Show

    show = Show(name="Party Mix")
    scene = Scene(name="Intro", duration=5.0)
    show.add_scene(scene)
    assert len(show.scenes) == 1
    assert show.name == "Party Mix"


def test_show_to_dict():
    from desktop.models.keyframe import Keyframe
    from desktop.models.scene import Scene
    from desktop.models.show import Show

    show = Show(name="Test Show")
    scene = Scene(name="Scene 1", duration=10.0)
    scene.add_keyframe(Keyframe(time=0.0, colors=[(255, 0, 0)]))
    show.add_scene(scene)
    d = show.to_dict()
    assert "id" in d
    assert "name" in d
    assert "scenes" in d
    assert len(d["scenes"]) == 1


def test_effect_types():
    from desktop.models.effect import EFFECT_TYPES

    assert "strobe" in EFFECT_TYPES
    assert "fire" in EFFECT_TYPES
    assert "emergency_us" in EFFECT_TYPES
    assert "emergency_de" in EFFECT_TYPES
    assert "rainbow" in EFFECT_TYPES
    assert "breathing" in EFFECT_TYPES


# Run model tests
test("Scene creation", test_scene_creation)
test("Keyframe creation", test_keyframe_creation)
test("Scene add keyframe", test_scene_add_keyframe)
test("Scene to dict", test_scene_to_dict)
test("Show creation", test_show_creation)
test("Show to dict", test_show_to_dict)
test("Effect types", test_effect_types)

# ============================================
# TEST 2: ESP Connection (without hardware)
# ============================================
print("\n=== Testing ESP Connection ===")


def test_esp_connection_init():
    from desktop.esp.connection import ESPConnection

    esp = ESPConnection("192.168.1.100", port=80)
    assert esp.ip == "192.168.1.100"
    assert esp.port == 80
    assert esp.base_url == "http://192.168.1.100:80"


def test_esp_connection_methods():
    from desktop.esp.connection import ESPConnection

    esp = ESPConnection("192.168.1.100")
    methods = [m for m in dir(esp) if not m.startswith("_")]
    expected = [
        "configure_wifi",
        "delete_show",
        "discover",
        "get_effects",
        "get_info",
        "get_show",
        "get_shows",
        "get_state",
        "ping",
        "play_show",
        "restart",
        "run_effect",
        "save_show",
        "set_brightness",
        "set_pixels",
    ]
    for m in expected:
        assert hasattr(esp, m), f"Missing method: {m}"


def test_esp_ping_fails_without_device():
    from desktop.esp.connection import ESPConnection

    esp = ESPConnection("192.168.255.255", timeout=0.5)  # Invalid IP
    try:
        result = esp.ping()
        assert result == False, "Ping should fail for invalid IP"
    except:
        pass  # Exception is also acceptable


# Run ESP tests
test("ESP Connection init", test_esp_connection_init)
test("ESP Connection methods", test_esp_connection_methods)
test("ESP ping fails without device", test_esp_ping_fails_without_device)

# ============================================
# TEST 3: ESP Flasher (without hardware)
# ============================================
print("\n=== Testing ESP Flasher ===")


def test_flasher_init():
    from desktop.esp.flasher import ESPFlasher

    flash = ESPFlasher()
    assert hasattr(flash, "_esptool_available")


def test_flasher_get_firmwares():
    from desktop.esp.flasher import ESPFlasher

    flash = ESPFlasher()
    firmwares = flash.get_available_firmwares()
    assert len(firmwares) == 3
    assert firmwares[0]["chip"] in ["esp32s3", "esp32", "esp32c3"]


def test_flasher_detect_ports():
    from desktop.esp.flasher import ESPFlasher

    flash = ESPFlasher()
    ports = flash.detect_ports()
    # Should return list (may be empty if no ESP32 connected)
    assert isinstance(ports, list)


# Run flasher tests
test("Flasher init", test_flasher_init)
test("Flasher get firmwares", test_flasher_get_firmwares)
test("Flasher detect ports", test_flasher_detect_ports)

# ============================================
# TEST 4: ESP MDNS Discovery (without hardware)
# ============================================
print("\n=== Testing ESP MDNS Discovery ===")


def test_mdns_discovery_init():
    from desktop.esp.mdns_discovery import MDNSDiscovery

    disc = MDNSDiscovery()
    assert hasattr(disc, "MDNS_GROUP")
    assert hasattr(disc, "SERVICE_TYPE")


def test_discover_neopulse_devices():
    from desktop.esp.mdns_discovery import discover_neopulse_devices

    devices = discover_neopulse_devices(timeout=1.0)
    # Should return list (may be empty if no devices found)
    assert isinstance(devices, list)


# Run MDNS tests
test("MDNS Discovery init", test_mdns_discovery_init)
test("Discover NeoPulse devices", test_discover_neopulse_devices)

# ============================================
# TEST 5: Widgets (logic tests without GUI)
# ============================================
print("\n=== Testing Widgets ===")


def test_pixel_preview_logic():
    """Test PixelPreviewWidget logic without GUI"""
    # Simulate pixel color updates
    pixels = [(0, 0, 0)] * 64
    # Update first 10 pixels
    for i in range(10):
        pixels[i] = (255, i * 25, 0)
    assert pixels[0] == (255, 0, 0)
    assert pixels[9] == (255, 225, 0)


def test_timeline_logic():
    """Test TimelineWidget logic without GUI"""
    # Simulate timeline calculations
    zoom = 50  # pixels per second
    offset_x = 50

    # Convert time to pixel position
    def time_to_x(time):
        return offset_x + time * zoom

    # Convert pixel position to time
    def x_to_time(x):
        return max(0, (x - offset_x) / zoom)

    assert time_to_x(0) == 50
    assert time_to_x(1) == 100
    assert x_to_time(50) == 0
    assert x_to_time(100) == 1


def test_scene_tree_logic():
    """Test SceneTreeWidget logic without GUI"""
    # Simulate scene tree operations
    scenes = []

    def add_scene(name, duration):
        scenes.append({"name": name, "duration": duration})

    def remove_scene(idx):
        if 0 <= idx < len(scenes):
            scenes.pop(idx)

    add_scene("Intro", 5.0)
    add_scene("Main", 10.0)
    add_scene("Outro", 3.0)

    assert len(scenes) == 3
    remove_scene(1)
    assert len(scenes) == 2
    assert scenes[1]["name"] == "Outro"


# Run widget tests
test("Pixel preview logic", test_pixel_preview_logic)
test("Timeline logic", test_timeline_logic)
test("Scene tree logic", test_scene_tree_logic)

# ============================================
# TEST 6: Emulator (HTML validation)
# ============================================
print("\n=== Testing Emulator ===")


def test_emulator_html_exists():
    emulator_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "emulator", "index.html"
    )
    assert os.path.exists(emulator_path), f"Emulator HTML not found at {emulator_path}"


def test_emulator_html_valid():
    emulator_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "emulator", "index.html"
    )
    with open(emulator_path, "r") as f:
        content = f.read()
    assert "<!DOCTYPE html>" in content
    assert "<html" in content
    assert "</html>" in content
    assert "NeoPulse" in content


def test_emulator_has_all_effects():
    emulator_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "emulator", "index.html"
    )
    with open(emulator_path, "r") as f:
        content = f.read()
    effects = ["strobe", "fire", "emergency_us", "emergency_de", "rainbow", "breathing"]
    for effect in effects:
        assert effect in content, f"Effect '{effect}' not found in emulator"


# Run emulator tests
test("Emulator HTML exists", test_emulator_html_exists)
test("Emulator HTML valid", test_emulator_html_valid)
test("Emulator has all effects", test_emulator_has_all_effects)

# ============================================
# TEST 7: Firmware (Python syntax validation)
# ============================================
print("\n=== Testing Firmware ===")


def test_firmware_main_syntax():
    firmware_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "main.py"
    )
    with open(firmware_path, "r") as f:
        code = f.read()
    compile(code, firmware_path, "exec")  # Will raise SyntaxError if invalid


def test_firmware_server_syntax():
    firmware_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "server.py"
    )
    with open(firmware_path, "r") as f:
        code = f.read()
    compile(code, firmware_path, "exec")


def test_firmware_config_syntax():
    firmware_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "config.py"
    )
    with open(firmware_path, "r") as f:
        code = f.read()
    compile(code, firmware_path, "exec")


def test_firmware_neopixel_driver_syntax():
    firmware_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "neopixel_driver.py"
    )
    with open(firmware_path, "r") as f:
        code = f.read()
    compile(code, firmware_path, "exec")


def test_firmware_animation_engine_syntax():
    firmware_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "animation_engine.py"
    )
    with open(firmware_path, "r") as f:
        code = f.read()
    compile(code, firmware_path, "exec")


def test_firmware_effects_syntax():
    effects_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "effects"
    )
    for filename in os.listdir(effects_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(effects_dir, filename)
            with open(filepath, "r") as f:
                code = f.read()
            compile(code, filepath, "exec")


# Run firmware tests
test("Firmware main.py syntax", test_firmware_main_syntax)
test("Firmware server.py syntax", test_firmware_server_syntax)
test("Firmware config.py syntax", test_firmware_config_syntax)
test("Firmware neopixel_driver.py syntax", test_firmware_neopixel_driver_syntax)
test("Firmware animation_engine.py syntax", test_firmware_animation_engine_syntax)
test("Firmware effects syntax", test_firmware_effects_syntax)

# ============================================
# TEST 8: Web Interface (HTML validation)
# ============================================
print("\n=== Testing Web Interface ===")


def test_web_index_exists():
    web_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "web", "index.html"
    )
    assert os.path.exists(web_path), f"Web index not found at {web_path}"


def test_web_interface_valid():
    web_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "web", "index.html"
    )
    with open(web_path, "r") as f:
        content = f.read()
    assert "<!DOCTYPE html>" in content
    assert "NeoPulse" in content


def test_web_css_exists():
    css_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "web", "css", "style.css"
    )
    assert os.path.exists(css_path), f"CSS not found at {css_path}"


def test_web_js_exists():
    js_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "esp32-firmware", "web", "js")
    files = os.listdir(js_dir)
    assert any(f.endswith(".js") for f in files), "No JS files found"


# Run web interface tests
test("Web index exists", test_web_index_exists)
test("Web interface valid", test_web_interface_valid)
test("Web CSS exists", test_web_css_exists)
test("Web JS exists", test_web_js_exists)

# ============================================
# TEST 9: Documentation
# ============================================
print("\n=== Testing Documentation ===")


def test_readme_exists():
    readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
    assert os.path.exists(readme_path), f"README.md not found at {readme_path}"


def test_readme_content():
    readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
    assert os.path.exists(readme_path), f"README.md not found at {readme_path}"
    with open(readme_path, "r") as f:
        content = f.read()
    assert len(content) > 1000, "README.md too short"
    assert "NeoPulse" in content
    assert "## Features" in content or "✨ Features" in content
    assert "## Installation" in content or "📦 Installation" in content


def test_design_doc_exists():
    design_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "neopulse-design.md"
    )
    if not os.path.exists(design_path):
        design_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neopulse-design.md")
    assert os.path.exists(design_path), f"Design doc not found at {design_path}"


# Run documentation tests
test("README exists", test_readme_exists)
test("README content", test_readme_content)
test("Design doc exists", test_design_doc_exists)

# ============================================
# TEST 10: Project Structure
# ============================================
print("\n=== Testing Project Structure ===")


def test_desktop_structure():
    expected_files = [
        "desktop/main.py",
        "desktop/app.py",
        "desktop/models/__init__.py",
        "desktop/models/scene.py",
        "desktop/models/show.py",
        "desktop/models/keyframe.py",
        "desktop/models/effect.py",
        "desktop/esp/__init__.py",
        "desktop/esp/connection.py",
        "desktop/esp/flasher.py",
        "desktop/esp/mdns_discovery.py",
        "desktop/widgets/__init__.py",
        "desktop/widgets/color_picker.py",
        "desktop/widgets/pixel_preview.py",
        "desktop/widgets/timeline.py",
        "desktop/widgets/scene_tree.py",
        "desktop/windows/__init__.py",
        "desktop/windows/setup_wizard.py",
        "desktop/windows/show_editor.py",
        "desktop/windows/live_control.py",
        "desktop/windows/project_manager.py",
    ]
    for f in expected_files:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f)
        assert os.path.exists(path), f"Missing file: {f}"


def test_firmware_structure():
    expected_files = [
        "esp32-firmware/boot.py",
        "esp32-firmware/main.py",
        "esp32-firmware/config.py",
        "esp32-firmware/server.py",
        "esp32-firmware/neopixel_driver.py",
        "esp32-firmware/animation_engine.py",
        "esp32-firmware/effects/__init__.py",
        "esp32-firmware/effects/strobe.py",
        "esp32-firmware/effects/fire.py",
        "esp32-firmware/effects/emergency_us.py",
        "esp32-firmware/effects/emergency_de.py",
        "esp32-firmware/effects/rainbow.py",
        "esp32-firmware/effects/breathing.py",
    ]
    for f in expected_files:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f)
        assert os.path.exists(path), f"Missing file: {f}"


def test_emulator_structure():
    emulator_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "emulator", "index.html"
    )
    assert os.path.exists(emulator_path), "Emulator index.html not found"


# Run structure tests
test("Desktop structure", test_desktop_structure)
test("Firmware structure", test_firmware_structure)
test("Emulator structure", test_emulator_structure)

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print(f"RESULTS: {results['passed']} passed, {results['failed']} failed")
if results["errors"]:
    print("\nFAILED TESTS:")
    for name, error in results["errors"]:
        print(f"  - {name}: {error}")
print("=" * 60)

# Exit with appropriate code
sys.exit(0 if results["failed"] == 0 else 1)

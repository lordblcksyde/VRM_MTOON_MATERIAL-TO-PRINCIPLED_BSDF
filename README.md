# VRM Material & Alpha Fixer for Blender

[![Blender](https://img.shields.io/badge/Blender-4.0%20%7C%204.2%20%7C%204.5%20%7C%205.0%20%7C%205.2+-orange?logo=blender&logoColor=white)](https://www.blender.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A lightweight Blender add-on located in the 3D Viewport Sidebar (**N-Panel**) to automatically fix imported **VRM / Anime / VTuber avatar materials** in standard Blender (Cycles, EEVEE, and EEVEE Next).

Disables incompatible MToon shaders, fixes broken texture alpha channels, maps textures to emission with customizable brightness, and resets roughness to eliminate unnatural glossy reflections.

---

## 📌 The Problem It Solves

- Converts the Default Mtoon Shader to Principled Bsdf and also assigns the Image Texture to its Emission socket (You can set it to 0 if you don't want it)

---

## ✨ Features

- ⚡ **N-Panel 3D Viewport Integration**: Quick-access panel in the `VRM Fix` tab of your Sidebar (<kbd>N</kbd> key).
- 🧩 **Alpha & MToon Fixer**:
  - Automatically disables `m.vrm_addon_extension.mtoon1.enabled` so materials use standard **Principled BSDF**.
  - Finds the Base Color Image Texture and wires its **Alpha** output directly into **Principled BSDF Alpha**.
  - Sets the material surface render method to **`DITHERED`** (and blend mode to **`CLIP`**), preventing transparency depth-sorting glitches in EEVEE Next and Blender 4.2+.
- 💡 **Emission & Roughness Setup**:
  - Automatically routes the Base Color texture into the shader's **Emission Color** / **Emission** socket.
  - **Interactive Emission Strength Slider**: Fine-tune character brightness directly from the panel (default: `0.50`).
  - **Custom Roughness Slider**: Unlinks roughness maps and sets uniform matte roughness (default: `1.00`) to eliminate plastic reflections.
- 🎯 **Flexible Scope**:
  - **`Fix All`**: Processes every material in the blend file.
  - **`Selected`**: Applies only to the materials attached to currently selected meshes/objects (leaving environment/props untouched).
- 🚀 **1-Click Full Setup**: Run all steps in a single button click.
- ↩️ **Full Undo Support**: Safe to use; undo anytime with <kbd>Ctrl</kbd> + <kbd>Z</kbd>.

---

## 📥 Installation

### Method 1: Install from ZIP (Recommended)
1. Download [`vrm_material_alpha_fixer.zip`](https://github.com/lordblcksyde/VRM-BLENDER-MATERIAL-FIX/raw/main/vrm_material_alpha_fixer.zip) from this repository.
2. Open Blender.
3. Go to **Edit > Preferences > Add-ons**.
4. Click the dropdown arrow in the top right (or the **Install...** / **Install from Disk...** button).
5. Select the downloaded `.zip` file.
6. Enable the checkbox for **"VRM Material & Alpha Fixer"**.

### Method 2: Manual Installation
Copy [`vrm_material_alpha_fixer.py`](vrm_material_alpha_fixer.py) into your Blender addons directory:

- **Windows**:
  ```text
  %APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\
  ```
- **macOS**:
  ```text
  ~/Library/Application Support/Blender/<version>/scripts/addons/
  ```
- **Linux**:
  ```text
  ~/.config/blender/<version>/scripts/addons/
  ```

Then open Blender, go to **Preferences > Add-ons**, and enable **"VRM Material & Alpha Fixer"**.

---

## 🎮 How to Use

1. Open your Blender scene with your imported VRM avatar.
2. In the **3D Viewport**, press <kbd>N</kbd> to open the Sidebar.
3. Click on the **VRM Fix** tab.

```
┌───────────────────────────────────────┐
│           VRM Material Fixer          │
├───────────────────────────────────────┤
│ ▼ 1. Alpha & MToon Fix                │
│   [ Fix Alpha (All) ]  [ Selected ]   │
│                                       │
│ ▼ 2. Emission & Roughness             │
│   Emission Strength: [ 0.50 ◀───▶ ]   │
│   Roughness:         [ 1.00 ◀───▶ ]   │
│   [ Fix Emission (All) ] [ Selected ] │
│                                       │
│ ───────────────────────────────────── │
│   [ ✔ Run Full Fix (All Steps) ]      │
└───────────────────────────────────────┘
```

### Controls Breakdown

| Control | Description |
| :--- | :--- |
| **Fix Alpha (All)** | Disables MToon & connects texture Alpha to Principled BSDF Alpha for all materials. |
| **Fix Alpha (Selected)** | Same as above, but only for materials on currently selected objects. |
| **Emission Strength** | Numeric slider controlling self-illumination (default `0.50`). |
| **Roughness** | Numeric slider setting character surface roughness (default `1.00` for matte anime finish). |
| **Fix Emission (All / Selected)** | Connects Base Color texture to Emission and sets Roughness. |
| **Run Full Fix (All Steps)** | Runs both Alpha fix and Emission/Roughness setup in a single click. |

---

## 🛠 Under the Hood: What the Code Does

### 1. Alpha & MToon Fix
```python
# Disables VRM MToon extension
m.vrm_addon_extension.mtoon1.enabled = False

# Connects Image Texture Alpha to Principled BSDF Alpha
src = base.links[0].from_node
if src.type == 'TEX_IMAGE' and 'Alpha' in src.outputs:
    m.node_tree.links.new(src.outputs['Alpha'], bsdf.inputs['Alpha'])

# Sets DITHERED transparency for clean rendering in EEVEE Next
m.surface_render_method = 'DITHERED'
```

### 2. Emission & Roughness Setup
```python
# Connects Texture Color to Emission socket
m.node_tree.links.new(src.outputs['Color'], emission_socket)
strength.default_value = emission_strength  # Configurable (default 0.5)

# Clears roughness links and sets uniform matte roughness
roughness.default_value = roughness_val      # Configurable (default 1.0)
```

---

## 🔍 Compatibility

- **Blender**: 4.0, 4.1, 4.2 LTS, 4.3, 4.5, 5.0, 5.2+ (also compatible with 3.x and 2.8x)
- **Render Engines**: EEVEE Next, Cycles, EEVEE Legacy
- **OS**: Windows, macOS, Linux

---

## 📄 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

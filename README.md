# bpy-renderer

A go-to library for rendering 3D scenes and animations. Whether you're looking for a simple rendering script for demos or producing multi-view image datasets for training, **bpy-renderer** is a modular toolbox that supports both.

---

## ✨ Features

Bpy-renderer offers two core components:

- **Core package** for configuring engines, cameras, environments, models, scenes, and rendering outputs.
- **Example scripts** for common rendering tasks.

---

## 🎬 Demos

### 3D Object
https://github.com/user-attachments/assets/6e5a5767-0323-40aa-95a7-f1ab465976d6

### 3D Scene
https://github.com/user-attachments/assets/d68cf607-3769-487d-9cc7-9c8da311abb6

### 3D Animation
https://github.com/user-attachments/assets/2c7e356c-be30-4d73-bce8-2d9a9965a482  
https://github.com/user-attachments/assets/bda030ee-9144-4cb4-bab0-0fb2082180b8

---

## ⚙️ Installation

### 1. Clone & Install Python Package

We recommend using **Python 3.10**:

```bash
git clone https://github.com/huanngzh/bpy-renderer.git
cd bpy-renderer
pip install -e .
```
### 2. Create Directory
```bash
mkdir -p external && cd external

BLENDER_VERSION="3.6.5"
BLENDER_DIR="blender-$BLENDER_VERSION-linux-x64"
DOWNLOAD_URL="https://download.blender.org/release/Blender3.6/$BLENDER_DIR.tar.xz"

echo "Installing Blender $BLENDER_VERSION..."

if [ ! -d "$BLENDER_DIR" ]; then
    wget $DOWNLOAD_URL
    tar -xf "$BLENDER_DIR.tar.xz"
    rm "$BLENDER_DIR.tar.xz"
else
    echo "Blender already installed."
fi

cd ..

```bash
### 3. Run for 1 model
PYTHONPATH=./src ./external/blender-3.6.5-linux-x64/blender \
  --background \
  --python examples/object/render_6ortho.py

```

```bash
### 3. Run for 1 model
PYTHONPATH=./src ./external/blender-3.6.5-linux-x64/blender \
  --background \
  --python examples/object/render_dataset.py

```
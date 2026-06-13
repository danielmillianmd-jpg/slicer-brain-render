<div align="center">

# 🧠 NeuroVolume — Scripted 3D Brain MRI Rendering in Slicer

**A fully automated [3D Slicer](https://www.slicer.org/) pipeline that turns a raw DICOM study into a presentation-grade volume render — without a single manual click.**

[![Live Demo](https://img.shields.io/badge/Live-Demo_Page-2ea44f?style=for-the-badge)](https://danielmillianmd-jpg.github.io/slicer-brain-render/)
[![3D Slicer](https://img.shields.io/badge/3D_Slicer-5.10-e2792b?style=for-the-badge&logo=slickpic&logoColor=white)](https://www.slicer.org/)
[![Python](https://img.shields.io/badge/Python-Scripted-3776AB?style=for-the-badge&logo=python&logoColor=white)](#how-it-works)
[![VTK](https://img.shields.io/badge/Rendering-VTK-cc0000?style=for-the-badge)](https://vtk.org/)

</div>

---

## Why this exists

Anyone can load a scan and click "Volume Rendering." The hard part — and the part worth showing — is doing it **reproducibly**: a script that ingests an arbitrary DICOM study, picks the best series automatically, applies a proper transfer function, frames the camera, and exports publication-ready images every time, identically. That script is this repository.

> **Educational / portfolio use only.** Built from a de-identified teaching study. Not a medical device; not for diagnostic use.

---

## Contents

- [Renders](#renders)
- [How it works](#how-it-works)
- [Tech stack](#tech-stack)
- [Run it yourself](#run-it-yourself)
- [Data & provenance](#data--provenance)

---

## Renders

### 1 · Anatomical volume render — FLAIR
Head reconstructed by volume-rendering the FLAIR acquisition, framed at a 3/4 oblique angle with a studio background and orientation marker.

![Anatomical volume render](images/01_volume_render_anatomy.png)

### 2 · Contrast-enhanced T1
The post-contrast T1 series. Its limited through-plane coverage (~48 mm) reads honestly as a cross-sectional slab — a real property of a clinical 2D acquisition, not an isotropic volume.

![Contrast-enhanced volume render](images/02_volume_render_contrast.png)

### 3 · Four-up MPR + 3D
Standard radiology reading layout: axial, coronal, and sagittal multiplanar reconstruction beside the live 3D volume.

![Four-up MPR](images/03_fourup_MPR.png)

---

## How it works

The pipeline (`scripts/build_scene.py`) runs end-to-end in headless or GUI Slicer:

| Step | What the script does |
|------|----------------------|
| **1 · Ingest** | Imports every series of the study into a temporary Slicer DICOM database |
| **2 · Select** | Chooses the hero volume by 3D coverage (through-plane extent) and a secondary by in-plane resolution / contrast — no hard-coded series names |
| **3 · Render** | Applies Slicer's `MR-Default` transfer function to each volume's property node |
| **4 · Frame** | Computes a 3/4 oblique camera from the volume's RAS bounds for a consistent hero shot |
| **5 · Capture** | Exports high-resolution PNGs of the 3D view and the four-up MPR layout via `ScreenCapture` |
| **6 · Bundle** | Saves the whole scene as a portable, self-contained `.mrb` |

`scripts/finalize_scene.py` reopens the bundle, sets a polished default view, and re-saves — so the `.mrb` opens straight to the hero render.

---

## Tech stack

- **3D Slicer 5.10** — medical imaging platform (VTK + ITK + Qt under the hood)
- **Python** — Slicer's scripting interface (`slicer`, `DICOMLib`, `ScreenCapture`, `vtkMRML*`)
- **VTK GPU volume rendering** — `MR-Default` transfer-function preset
- **DICOM** — multi-series MR study ingest via a temporary Slicer DICOM database

---

## Run it yourself

```bash
# 1. Point the script at any DICOM study directory (edit DICOM_DIR at the top)
# 2. Run it — GUI or headless:
Slicer --python-script scripts/build_scene.py
```

**Suggested flow once it opens:**
1. The hero head render appears in the 3D view — drag to rotate.
2. Toggle the secondary contrast volume in the Volume Rendering module.
3. Switch to the four-up layout to scrub axial/coronal/sagittal planes.
4. Re-run anytime — the output is deterministic.

*Requires 3D Slicer 5.x. The pipeline is dataset-agnostic and will produce a comparable scene from any volumetric DICOM study.*

---

## Data & provenance

The input is a **de-identified** clinical brain MRI: anisotropic 2D acquisitions (15–30 slices, 2–4 mm thick), not a high-resolution isotropic volume. The FLAIR series carries enough through-plane coverage for a convincing head render; the thinner contrast series renders as a slab. This limitation is the *data's*, not the pipeline's — and it's documented here deliberately, because being honest about acquisition geometry is part of doing imaging work properly.

<div align="center">

---

*Built by Daniel Millian · scripted Slicer + Python · 2026*

</div>

"""
Build a professional 3D Slicer scene from the deidentified brain MRI.
Loads all 7 series, volume-renders the best-coverage and the contrast series
from a 3/4 oblique angle, captures high-res screenshots + a 4-up MPR montage,
and saves a .mrb scene bundle.
Run:  Slicer --python-script build_scene.py
"""
import os, slicer
from DICOMLib import DICOMUtils

DICOM_DIR = "/Users/drdanielmillian/Desktop/Reference Files 6.6.26/Radiology Imaging - DEIDENTIFIED"
OUT_DIR   = "/Users/drdanielmillian/Desktop/Slicer_Brain_Scene"
os.makedirs(OUT_DIR, exist_ok=True)

def log(m): print("[SCENE] " + m)

# --- Make the window big so captures are high resolution ------------------
mw = slicer.util.mainWindow()
mw.showNormal(); mw.resize(1920, 1200)
slicer.app.processEvents()

# --- 1. Load every series -------------------------------------------------
loaded = []
with DICOMUtils.TemporaryDICOMDatabase() as db:
    DICOMUtils.importDicom(DICOM_DIR, db)
    for puid in db.patients():
        loaded.extend(DICOMUtils.loadPatientByUID(puid))

volumes = [slicer.mrmlScene.GetNodeByID(n) for n in loaded]
volumes = [v for v in volumes if v and v.IsA("vtkMRMLScalarVolumeNode")]
log("loaded %d volume(s)" % len(volumes))

def coverage(v):
    img = v.GetImageData()
    if not img: return 0
    sp = v.GetSpacing(); d = img.GetDimensions()
    return sp[2] * d[2]                      # through-plane extent (mm)

for v in volumes:
    log("  %-26s coverage=%5.0f mm" % (v.GetName(), coverage(v)))

# Hero for the "anatomy" render = best 3D coverage (FLAIR here)
hero = max(volumes, key=coverage)
# Secondary render = contrast-enhanced T1, highest in-plane res
contrast = max(
    [v for v in volumes if "POST" in v.GetName().upper()] or volumes,
    key=lambda v: (v.GetImageData().GetDimensions()[0] if v.GetImageData() else 0),
)
log("hero=%s  contrast=%s" % (hero.GetName(), contrast.GetName()))

vrLogic = slicer.modules.volumerendering.logic()

def setup_vr(vol, preset_name="MR-Default"):
    disp = vrLogic.CreateDefaultVolumeRenderingNodes(vol)
    vrLogic.UpdateDisplayNodeFromVolumeNode(disp, vol)
    preset = vrLogic.GetPresetByName(preset_name)
    if preset:
        disp.GetVolumePropertyNode().GetVolumeProperty().DeepCopy(preset.GetVolumeProperty())
    disp.SetVisibility(False)
    return disp

vr_nodes = {v.GetID(): setup_vr(v) for v in {hero.GetID(): hero, contrast.GetID(): contrast}.values()}

# --- 2. Professional 3D view styling --------------------------------------
lm = slicer.app.layoutManager()
view3d = lm.threeDWidget(0).threeDView()
vnode = view3d.mrmlViewNode()
vnode.SetBackgroundColor(0.10, 0.11, 0.14)
vnode.SetBackgroundColor2(0.02, 0.02, 0.04)
vnode.SetBoxVisible(False)
vnode.SetAxisLabelsVisible(False)
try:
    vnode.SetOrientationMarkerType(vnode.OrientationMarkerTypeHuman)
    vnode.SetOrientationMarkerSize(vnode.OrientationMarkerSizeMedium)
    vnode.SetRulerType(vnode.RulerTypeThin)
except Exception as e:
    log("styling skipped: %s" % e)

camNode = slicer.util.getNodesByClass("vtkMRMLCameraNode")[0]

def oblique_camera(vol):
    b = [0]*6; vol.GetRASBounds(b)
    cx, cy, cz = (b[0]+b[1])/2, (b[2]+b[3])/2, (b[4]+b[5])/2
    diag = ((b[1]-b[0])**2 + (b[3]-b[2])**2 + (b[5]-b[4])**2) ** 0.5
    camNode.SetFocalPoint(cx, cy, cz)
    # anterior, slightly right and above -> 3/4 portrait view
    camNode.SetPosition(cx + diag*0.55, cy + diag*1.05, cz + diag*0.45)
    camNode.SetViewUp(0, 0, 1)
    camNode.ResetClippingRange()

import ScreenCapture
cap = ScreenCapture.ScreenCaptureLogic()

def render_volume(vol, outname):
    for nid, dn in vr_nodes.items():
        dn.SetVisibility(nid == vol.GetID())
    lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
    slicer.app.processEvents()
    oblique_camera(vol)
    view3d.forceRender(); slicer.app.processEvents()
    path = os.path.join(OUT_DIR, outname)
    cap.captureImageFromView(view3d, path)
    log("saved " + outname)

render_volume(hero,     "01_volume_render_anatomy.png")
render_volume(contrast, "02_volume_render_contrast.png")

# --- 3. Four-up MPR montage (full layout) ---------------------------------
slicer.util.setSliceViewerLayers(background=contrast, fit=True)
lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
slicer.app.processEvents()
# keep the contrast VR visible in the 3D quadrant
for nid, dn in vr_nodes.items():
    dn.SetVisibility(nid == contrast.GetID())
for c in ("Red", "Yellow", "Green"):
    w = lm.sliceWidget(c)
    if w: w.sliceController().fitSliceToBackground()
oblique_camera(contrast)
view3d.forceRender(); slicer.app.processEvents()
cap.captureImageFromView(None, os.path.join(OUT_DIR, "03_fourup_MPR.png"))
log("saved 03_fourup_MPR.png")

# --- 4. Leave a clean 4-up scene and save the bundle ----------------------
mrb = os.path.join(OUT_DIR, "Brain_MRI_Scene.mrb")
ok = slicer.util.saveScene(mrb)
log("saveScene -> %s" % ok)

with open(os.path.join(OUT_DIR, "_DONE.txt"), "w") as f:
    f.write("hero=%s contrast=%s volumes=%d mrb=%s\n" %
            (hero.GetName(), contrast.GetName(), len(volumes), ok))
log("DONE")

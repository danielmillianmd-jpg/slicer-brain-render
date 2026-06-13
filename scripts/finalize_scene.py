"""Open the saved scene, set a polished default view (FLAIR head in 3D),
re-save the .mrb, and leave Slicer open for interactive use."""
import os, slicer

OUT_DIR = "/Users/drdanielmillian/Desktop/Slicer_Brain_Scene"
MRB = os.path.join(OUT_DIR, "Brain_MRI_Scene.mrb")

slicer.util.loadScene(MRB)
mw = slicer.util.mainWindow(); mw.showMaximized()

vols = slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode")
flair = next((v for v in vols if "FLAIR" in v.GetName().upper()), vols[0])

# show only the FLAIR volume rendering
for dn in slicer.util.getNodesByClass("vtkMRMLVolumeRenderingDisplayNode"):
    dn.SetVisibility(flair.GetID() in (dn.GetVolumeNodeID() or ""))

lm = slicer.app.layoutManager()
lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
slicer.app.processEvents()

view3d = lm.threeDWidget(0).threeDView()
camNode = slicer.util.getNodesByClass("vtkMRMLCameraNode")[0]
b = [0]*6; flair.GetRASBounds(b)
cx, cy, cz = (b[0]+b[1])/2, (b[2]+b[3])/2, (b[4]+b[5])/2
diag = ((b[1]-b[0])**2 + (b[3]-b[2])**2 + (b[5]-b[4])**2) ** 0.5
camNode.SetFocalPoint(cx, cy, cz)
camNode.SetPosition(cx + diag*0.55, cy + diag*1.05, cz + diag*0.45)
camNode.SetViewUp(0, 0, 1)
camNode.ResetClippingRange()
view3d.forceRender(); slicer.app.processEvents()

slicer.util.saveScene(MRB)
with open(os.path.join(OUT_DIR, "_DONE2.txt"), "w") as f:
    f.write("finalized default view = %s\n" % flair.GetName())
print("[SCENE] finalized, leaving Slicer open")

# Placeholder for 3D CAD files

STL files for 3D printing will be placed in this directory.

## Recommended File Organization

```
stl_files/
├── hands/
│   ├── left/
│   │   ├── palm.stl
│   │   ├── fingers.stl
│   │   └── thumb.stl
│   └── right/
│       └── (mirror of left)
├── arms/
│   ├── shoulder_assembly.stl
│   ├── upper_arm.stl
│   ├── elbow_joint.stl
│   └── forearm.stl
├── legs/
│   ├── hip_assembly.stl
│   ├── upper_leg.stl
│   ├── knee_joint.stl
│   ├── lower_leg.stl
│   └── ankle_foot.stl
├── torso/
│   ├── torso_front.stl
│   ├── torso_back.stl
│   └── electronics_bay.stl
└── head/
    ├── head_base.stl
    ├── head_pan_bracket.stl
    └── camera_mount.stl
```

## Print Settings

**Material:** PLA  
**Layer Height:** 0.2mm  
**Infill:** 30-40% for structural, 15% for cosmetic  
**Supports:** Yes for overhangs >45°  

See [Quick Start Guide](../../docs/quick_start.md) for detailed printing instructions.

---

**Note:** STL files will be added in future releases or can be sourced from InMoov-compatible designs.

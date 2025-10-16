# AI Models Directory

This directory contains trained models for computer vision.

## Required Models

### MobileNetV2-SSD (COCO)

Download the model:

```bash
cd models
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
unzip coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
mv detect.tflite mobilenet_ssd_v2.tflite
```

**Model Info:**
- Framework: TensorFlow Lite
- Input: 300×300 RGB
- Output: Bounding boxes + class IDs + confidence scores
- Classes: 90 (COCO dataset)
- Quantization: INT8 for fast inference

### COCO Labels

Create `coco_labels.txt`:
```bash
cat > coco_labels.txt << 'EOF'
person
bicycle
car
motorcycle
airplane
bus
train
truck
boat
traffic light
fire hydrant
stop sign
parking meter
bench
bird
cat
dog
horse
sheep
cow
elephant
bear
zebra
giraffe
backpack
umbrella
handbag
tie
suitcase
frisbee
skis
snowboard
sports ball
kite
baseball bat
baseball glove
skateboard
surfboard
tennis racket
bottle
wine glass
cup
fork
knife
spoon
bowl
banana
apple
sandwich
orange
broccoli
carrot
hot dog
pizza
donut
cake
chair
couch
potted plant
bed
dining table
toilet
tv
laptop
mouse
remote
keyboard
cell phone
microwave
oven
toaster
sink
refrigerator
book
clock
vase
scissors
teddy bear
hair drier
toothbrush
EOF
```

## Custom Model Training (Optional)

To train a custom model for fabric corner detection:

1. **Collect dataset** (~500+ images of fabric corners)
2. **Annotate** with tools like [CVAT](https://cvat.org) or [LabelImg](https://github.com/heartexlabs/labelImg)
3. **Train** using [TensorFlow Model Maker](https://www.tensorflow.org/lite/guide/model_maker)
4. **Export** to TFLite format
5. **Replace** `mobilenet_ssd_v2.tflite` and update labels

## Model Performance

**On Raspberry Pi 5:**
- Inference time: ~100-150ms per frame
- FPS: 6-10 (with display)
- Detection accuracy: ~70-80% on well-lit scenes

---

**Current Status:** Using pre-trained COCO model  
**Future Work:** Custom fabric corner detection model

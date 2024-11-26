# bottle-caps

The idea of this project it's to have a machine learning app that will detect and identify bottlecaps from a source.

## Overview

bottle-caps uses computer vision techniques, primarily based on OpenCV, to identify and match bottle caps. While the app currently operates locally, future plans include transitioning to cloud hosting. The app utilizes key OpenCV methods including **Simple Blob Detector**, **Hough Transform Circles**, **MobilNet**, each requiring specific preprocessing steps.

## Code Flow

Below is an overview of how the code operates.

### Database Creation

Currently, there is a script that generates all the data and uploads it to Pinecone, the vector database used to compare the vector result from the model and the ones from the database: `scripts/generate_model.py`.

### Blob Detection

Initially, the _Hough Transform Circles_ method was used, but it resulted in multiple false positives due to the variability in circle sizes. To resolve this, the _Simple Blob Detector_ was applied first. This process involves reducing the image's color depth to three levels _(photos should ideally be taken on a white background or with high-contrast caps)_. Overlapping blobs, which might represent multiple detections of the same cap, were removed. The median size of the blobs was calculated to ensure accuracy.

- **Why Median Over Average?** Using the median rather than the average prevents large or small false positives from skewing the results. Since all bottle caps have a diameter of 37mm, the median provides a more reliable measurement.

### Hough Transform Circles

Based on the approximate radius determined from the blobs, upper and lower bounds were set. Preprocessing was applied before using Hough Transform Circles to identify the positions of all circles in the image.

### MobilNet

Currently using a MobilNet model to identify the caps, basically transform them in vector format and then saving them in Pinecone. It is a vector database great for comparing AI content.

## Examples

### Detection

In the following images you can see how the detect method works and a small animation using the `visual` module.

<p align="center">
  <img src="https://github.com/user-attachments/assets/f5c6f3d3-348b-421b-9fcc-b9d8bd5354fb" width="200" />
  <img src="https://github.com/user-attachments/assets/c76a0694-b93e-405a-bb97-62de10ad9b26" width="200" />
  <img src="https://github.com/user-attachments/assets/5cef7d52-1785-4f36-aaac-e2213f0271b0" width="200" />
  <img src="https://github.com/user-attachments/assets/65d7d827-dc37-469c-8a43-fda371dde82b" width="200" />
</p>

### Identification
Identification model using only a pretrained MobilNet
<p align="center">
  <img src="https://github.com/user-attachments/assets/fe085892-0d36-4e2c-a0c3-02c309042f55" width="700" />
</p>

### Full Example

Below is an example output of the full model. The results show areas for improvement: while the first two caps are correctly identified, the bottom two are labeled incorrectly. Speed optimizations are also needed. For additional notes on testing, refer to `ScriptsMain/note_tests/README.md`.

![image](https://user-images.githubusercontent.com/51784809/232329262-603f6ff8-a1df-423a-bb16-22454085e084.png)

# Aditional notes

- The code from the visual folder was written with ChatGPT as I did not want to dive too much into the creation of `.gif` myself.

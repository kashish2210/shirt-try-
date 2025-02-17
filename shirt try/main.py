import os
import cvzone
import cv2
from cvzone.PoseModule import PoseDetector

cap = cv2.VideoCapture(r"Resources\Videos\1.mp4")
detector = PoseDetector()

shirtFolderPath = os.path.join("Resources", "Shirts")
print(shirtFolderPath)
listShirts = os.listdir(shirtFolderPath)
fixedRatio = 262 / 190  # widthOfShirt/widthOfPoint11to12
shirtRatioHeightWidth = 581 / 440
imageNumber = 0
imgButtonRight = cv2.imread(r"Resources\button.png", cv2.IMREAD_UNCHANGED)
imgButtonLeft = cv2.flip(imgButtonRight, 1)
counterRight = 0
counterLeft = 0
selectionSpeed = 10

while True:
    success, img = cap.read()
    if not success:
        print("Failed to read frame from video.")
        break

    img = detector.findPose(img)
    # img = cv2.flip(img, 1)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)
    if lmList:

        center = bboxInfo["center"]
        lm11 = lmList[11][0:2]
        lm12 = lmList[12][0:2]

        # Debugging prints
        print(f"lm11: {lm11}, lm12: {lm12}")

        widthOfShirt = int((lm11[0] - lm12[0]) * fixedRatio)
        print(f"Calculated widthOfShirt: {widthOfShirt}")

        if widthOfShirt > 0:
            imgShirtPath = os.path.join(shirtFolderPath, listShirts[imageNumber])
            print(f"Loading shirt image: {imgShirtPath}")
            imgShirt = cv2.imread(imgShirtPath, cv2.IMREAD_UNCHANGED)

            if imgShirt is not None:
                print(f"Loaded shirt image with shape: {imgShirt.shape}")
                imgShirt = cv2.resize(
                    imgShirt, (widthOfShirt, int(widthOfShirt * shirtRatioHeightWidth))
                )

                currentScale = (lm11[0] - lm12[0]) / 190
                offset = int(44 * currentScale), int(48 * currentScale)

                overlay_coords = (lm12[0] - offset[0], lm12[1] - offset[1])
                print(f"Overlay coordinates: {overlay_coords}")

                try:
                    img = cvzone.overlayPNG(img, imgShirt, overlay_coords)
                except Exception as e:
                    print(f"Error overlaying PNG: {e}")
            else:
                print("Failed to load shirt image.")

        img = cvzone.overlayPNG(img, imgButtonRight, (1074, 293))
        img = cvzone.overlayPNG(img, imgButtonLeft, (72, 293))

        if lmList[16][0] < 300:
            counterRight += 1
            cv2.ellipse(
                img,
                (139, 360),
                (66, 66),
                0,
                0,
                counterRight * selectionSpeed,
                (0, 255, 0),
                20,
            )
            if counterRight * selectionSpeed > 360:
                counterRight = 0
                if imageNumber < len(listShirts) - 1:
                    imageNumber += 1
        elif lmList[15][0] > 900:
            counterLeft += 1
            cv2.ellipse(
                img,
                (1138, 360),
                (66, 66),
                0,
                0,
                counterLeft * selectionSpeed,
                (0, 255, 0),
                20,
            )
            if counterLeft * selectionSpeed > 360:
                counterLeft = 0
                if imageNumber > 0:
                    imageNumber -= 1
        else:
            counterRight = 0
            counterLeft = 0

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
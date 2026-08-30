import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: root
    width: 800
    height: 600
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    parent: Overlay.overlay
    anchors.centerIn: parent

    property string imageSource: ""
    property real cropX: 0.0
    property real cropY: 0.0
    property real cropW: 1.0
    property real cropH: 1.0
    property real anchorX: 0.5
    property real anchorY: 0.5

    signal cropChanged(real x, real y, real w, real h)
    signal anchorChanged(real x, real y)

    onOpened: {
        initCrop();
    }

    onImageSourceChanged: {
        if (visible) {
            initCrop();
        }
    }

    background: Rectangle {
        color: "#1e1e1e"
        radius: 12
        border.color: "#d4365b"
        border.width: 2
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        Text {
            text: "Re-enquadrament i Ancoratge"
            color: "white"
            font.pixelSize: 18
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: "Usa la rodeta per fer zoom i arrossega per moure la imatge.\nMou el punt circular rosa per modificar el punt d'ancoratge."
            color: "#aaaaaa"
            font.pixelSize: 12
            Layout.alignment: Qt.AlignHCenter
        }

        Item {
            id: editorArea
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            Item {
                id: frame
                width: Math.min(parent.width - 40, (parent.height - 40) * 16 / 9)
                height: width * 9 / 16
                anchors.centerIn: parent
                z: 0 // Used for reference bounds
            }

            Image {
                id: image
                source: root.imageSource
                transformOrigin: Item.TopLeft
                z: 1

                property real minScale: 1.0

                onStatusChanged: {
                    if (status === Image.Ready) {
                        initCrop();
                    }
                }
            }

            // Dimming rectangles outside the 16:9 frame
            Item {
                z: 2
                anchors.fill: parent
                Rectangle {
                    color: "#A0000000"
                    x: 0
                    y: 0
                    width: parent.width
                    height: frame.y
                }
                Rectangle {
                    color: "#A0000000"
                    x: 0
                    y: frame.y + frame.height
                    width: parent.width
                    height: parent.height - (frame.y + frame.height)
                }
                Rectangle {
                    color: "#A0000000"
                    x: 0
                    y: frame.y
                    width: frame.x
                    height: frame.height
                }
                Rectangle {
                    color: "#A0000000"
                    x: frame.x + frame.width
                    y: frame.y
                    width: parent.width - (frame.x + frame.width)
                    height: frame.height
                }
            }

            // Frame border
            Rectangle {
                z: 3
                x: frame.x
                y: frame.y
                width: frame.width
                height: frame.height
                color: "transparent"
                border.color: "#d4365b"
                border.width: 2
            }

            MouseArea {
                id: imageDragArea
                anchors.fill: parent
                z: 4

                drag.target: image
                drag.minimumX: frame.x + frame.width - image.sourceSize.width * image.scale
                drag.maximumX: frame.x
                drag.minimumY: frame.y + frame.height - image.sourceSize.height * image.scale
                drag.maximumY: frame.y

                onWheel: function (wheel) {
                    if (image.sourceSize.width === 0)
                        return;
                    let zoomFactor = wheel.angleDelta.y > 0 ? 1.05 : 0.95;
                    let newScale = image.scale * zoomFactor;
                    newScale = Math.max(image.minScale, newScale);
                    newScale = Math.min(newScale, image.minScale * 5.0);

                    let mouseX = wheel.x;
                    let mouseY = wheel.y;

                    let relX = (mouseX - image.x) / image.scale;
                    let relY = (mouseY - image.y) / image.scale;

                    let newX = mouseX - relX * newScale;
                    let newY = mouseY - relY * newScale;

                    image.scale = newScale;
                    image.x = newX;
                    image.y = newY;

                    enforceBounds();
                    updateCrop();
                }

                onPositionChanged: {
                    if (drag.active)
                        updateCrop();
                }
            }

            // Anchor indicator (z: 5)
            Rectangle {
                id: anchorIndicator
                z: 5
                width: 24
                height: 24
                radius: 12
                color: "transparent"
                border.color: "#e9456c"
                border.width: 3
                x: frame.x + root.anchorX * frame.width - width / 2
                y: frame.y + root.anchorY * frame.height - height / 2

                Rectangle {
                    width: 6
                    height: 6
                    radius: 3
                    color: "#e9456c"
                    anchors.centerIn: parent
                }

                MouseArea {
                    anchors.fill: parent
                    drag.target: parent
                    drag.minimumX: frame.x - width / 2
                    drag.maximumX: frame.x + frame.width - width / 2
                    drag.minimumY: frame.y - height / 2
                    drag.maximumY: frame.y + frame.height - height / 2

                    onPositionChanged: {
                        if (drag.active) {
                            let nx = (parent.x + parent.width / 2 - frame.x) / frame.width;
                            let ny = (parent.y + parent.height / 2 - frame.y) / frame.height;
                            root.anchorChanged(nx, ny);
                        }
                    }
                }
            }
        }

        Button {
            text: "D'acord"
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 150
            Layout.preferredHeight: 40
            background: Rectangle {
                color: parent.down ? "#be2649" : (parent.hovered ? "#d4365b" : "#e9456c")
                radius: 8
            }
            contentItem: Text {
                text: parent.text
                color: "white"
                font.bold: true
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            onClicked: root.close()
        }
    }

    function initCrop() {
        if (image.sourceSize.width === 0)
            return;
        image.minScale = Math.max(frame.width / image.sourceSize.width, frame.height / image.sourceSize.height);

        if (root.cropW < 1.0 || root.cropH < 1.0) {
            image.scale = 1.0 / Math.max(root.cropW, root.cropH);
            image.x = frame.x - root.cropX * image.sourceSize.width * image.scale;
            image.y = frame.y - root.cropY * image.sourceSize.height * image.scale;
        } else {
            image.scale = image.minScale;
            image.x = frame.x + (frame.width - image.sourceSize.width * image.scale) / 2;
            image.y = frame.y + (frame.height - image.sourceSize.height * image.scale) / 2;
        }
        enforceBounds();
    }

    function enforceBounds() {
        let minX = frame.x + frame.width - image.sourceSize.width * image.scale;
        let maxX = frame.x;
        let minY = frame.y + frame.height - image.sourceSize.height * image.scale;
        let maxY = frame.y;

        image.x = Math.max(minX, Math.min(image.x, maxX));
        image.y = Math.max(minY, Math.min(image.y, maxY));
    }

    function updateCrop() {
        if (image.sourceSize.width === 0 || image.scale === 0)
            return;
        let totalW = image.sourceSize.width * image.scale;
        let totalH = image.sourceSize.height * image.scale;

        let cx = (frame.x - image.x) / totalW;
        let cy = (frame.y - image.y) / totalH;
        let cw = frame.width / totalW;
        let ch = frame.height / totalH;

        cx = Math.max(0, Math.min(cx, 1 - cw));
        cy = Math.max(0, Math.min(cy, 1 - ch));

        if (Math.abs(cx - root.cropX) > 0.001 || Math.abs(cy - root.cropY) > 0.001 || Math.abs(cw - root.cropW) > 0.001 || Math.abs(ch - root.cropH) > 0.001) {
            root.cropChanged(cx, cy, cw, ch);
        }
    }
}

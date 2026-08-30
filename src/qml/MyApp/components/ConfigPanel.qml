import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    color: "#ffffff"
    radius: 12
    border.color: "#b9b9b9"
    border.width: 1
    implicitHeight: layout.implicitHeight + 40

    property real photoDuration: photoDurationSlider.value
    property real transitionDuration: transitionDurationSlider.value
    property real zoomEnd: zoomEndSlider.value

    component PinkSlider: Slider {
        id: control
        snapMode: Slider.SnapAlways
        background: Rectangle {
            x: control.leftPadding
            y: control.topPadding + control.availableHeight / 2 - height / 2
            implicitWidth: 160
            implicitHeight: 6
            width: control.availableWidth
            height: implicitHeight
            radius: 3
            color: "#d7d7d5"
            Rectangle {
                width: control.visualPosition * parent.width
                height: parent.height
                color: "#e9456c"
                radius: 3
            }
        }
        handle: Rectangle {
            x: control.leftPadding + control.visualPosition * (control.availableWidth - width)
            y: control.topPadding + control.availableHeight / 2 - height / 2
            implicitWidth: 20
            implicitHeight: 20
            radius: 10
            color: control.pressed ? "#be2649" : (control.hovered ? "#d4365b" : "#e9456c")
            border.color: "white"
            border.width: 2
        }
    }

    ColumnLayout {
        id: layout
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15

        Text {
            text: "CONFIGURACIÓ GLOBAL"
            color: "#969798"
            font.pixelSize: 12
            font.bold: true
            font.letterSpacing: 1
        }

        RowLayout {
            spacing: 30
            Layout.fillWidth: true

            ColumnLayout {
                spacing: 2
                Layout.fillWidth: true
                Text {
                    text: "Duració foto: " + photoDurationSlider.value.toFixed(1) + " s"
                    color: "#000000"
                }
                PinkSlider {
                    id: photoDurationSlider
                    Layout.fillWidth: true
                    from: 1.0
                    to: 15.0
                    value: 5.0
                    stepSize: 0.5
                }
            }

            ColumnLayout {
                spacing: 2
                Layout.fillWidth: true
                Text {
                    text: "Transició: " + transitionDurationSlider.value.toFixed(1) + " s"
                    color: "#000000"
                }
                PinkSlider {
                    id: transitionDurationSlider
                    Layout.fillWidth: true
                    from: 0.0
                    to: 4.0
                    value: 1.5
                    stepSize: 0.5
                }
            }

            ColumnLayout {
                spacing: 2
                Layout.fillWidth: true
                Text {
                    text: "Zoom final: " + zoomEndSlider.value.toFixed(2) + "x"
                    color: "#000000"
                }
                PinkSlider {
                    id: zoomEndSlider
                    Layout.fillWidth: true
                    from: 1.00
                    to: 3.00
                    value: 1.20
                    stepSize: 0.05
                }
            }
        }
    }
}

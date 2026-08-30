import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

Popup {
    id: root
    property real extraHeight: 106 // Margins (20) + Spacing (20) + Header (30) + Footer (36)
    property real maxW: Math.min(parent.width * 0.9, 1280)
    property real maxH: parent.height * 0.9
    property bool constrainedByWidth: (maxW * 9 / 16 + extraHeight) <= maxH

    width: constrainedByWidth ? maxW : (maxH - extraHeight) * 16 / 9
    height: constrainedByWidth ? (maxW * 9 / 16 + extraHeight) : maxH
    anchors.centerIn: parent
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    property string videoSource: ""

    onOpened: {
        if (videoSource !== "") {
            player.play()
        }
    }
    
    onClosed: {
        player.stop()
    }

    onVideoSourceChanged: {
        if (visible && videoSource !== "") {
            player.play()
        }
    }

    background: Rectangle {
        color: "#1a1a1a"
        radius: 12
        border.color: "#333333"
        border.width: 1
    }

    MediaPlayer {
        id: player
        source: root.videoSource
        audioOutput: AudioOutput {}
        videoOutput: videoOut
        loops: MediaPlayer.Infinite
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            
            Text {
                text: "Vista Prèvia Ràpida"
                color: "white"
                font.pixelSize: 18
                font.bold: true
                Layout.fillWidth: true
            }
            
            Button {
                text: "X"
                onClicked: root.close()
                background: Rectangle {
                    color: parent.hovered ? "#ff0033" : "transparent"
                    radius: 4
                }
                contentItem: Image {
                    source: "../assets/close.svg"
                    sourceSize: Qt.size(20, 20)
                    fillMode: Image.PreserveAspectFit
                    horizontalAlignment: Image.AlignHCenter
                    verticalAlignment: Image.AlignVCenter
                }
                Layout.preferredWidth: 30
                Layout.preferredHeight: 30
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "black"

            VideoOutput {
                id: videoOut
                anchors.fill: parent
                fillMode: VideoOutput.PreserveAspectFit
            }
            
            Text {
                text: "Carregant preview..."
                color: "white"
                anchors.centerIn: parent
                visible: player.playbackState === MediaPlayer.StoppedState && videoSource !== ""
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter

            Button {
                text: player.playbackState === MediaPlayer.PlayingState ? "Pausa" : "Reprodueix"
                onClicked: {
                    if (player.playbackState === MediaPlayer.PlayingState) {
                        player.pause()
                    } else {
                        player.play()
                    }
                }
                background: Rectangle {
                    color: parent.down ? "#be2649" : (parent.hovered ? "#d4365b" : "#e9456c")
                    radius: 8
                    implicitHeight: 36
                    implicitWidth: 120
                }
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }
}

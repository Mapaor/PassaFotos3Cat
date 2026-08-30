import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Rectangle {
    Layout.fillWidth: true
    // When no video, make it massive
    Layout.preferredHeight: videoPath === "" ? 400 : 100
    color: "#ffffff"
    radius: 12
    border.color: "#b9b9b9"
    border.width: 1

    // Animate the height transition
    Behavior on Layout.preferredHeight {
        NumberAnimation {
            duration: 300
            easing.type: Easing.InOutQuad
        }
    }

    property string videoPath: ""
    property string outputName: ""
    property string outputDir: ""
    property string videoInfo: ""

    onVideoPathChanged: {
        if (videoPath !== "") {
            var path = videoPath.toString();
            if (path.startsWith("file:///")) {
                path = path.substring(8);
            }
            var nameWithExt = path.substring(path.lastIndexOf("/") + 1);
            var name = nameWithExt.substring(0, nameWithExt.lastIndexOf("."));
            if (name === "")
                name = nameWithExt;
            outputName = name + "_16x9";

            var dir = path.substring(0, path.lastIndexOf("/"));
            outputDir = "file:///" + dir;

            // Get info from backend synchronously since it is fast enough, or we could just call it.
            // videoConverter is exposed to QML.
            videoInfo = videoConverter.get_video_info(videoPath);
        } else {
            videoInfo = "";
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 15

        DropArea {
            Layout.fillWidth: true
            Layout.fillHeight: true
            onDropped: drop => {
                if (drop.hasUrls && drop.urls.length > 0) {
                    videoPath = drop.urls[0];
                }
            }
            Rectangle {
                anchors.fill: parent
                color: parent.containsDrag ? "#d4365b" : "transparent"
                opacity: parent.containsDrag ? 0.1 : 1.0
                radius: 8
                border.color: parent.containsDrag ? "#d4365b" : (videoPath === "" ? "#e9456c" : "#b9b9b9")
                border.width: videoPath === "" ? 2 : 1
            }

            // Empty State (Centered Drag & Drop)
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 15
                visible: videoPath === ""

                Button {
                    icon.source: "../assets/inbox.svg"
                    icon.color: parent.parent.containsDrag ? "#d4365b" : "#e9456c"
                    icon.width: 24
                    icon.height: 24
                    text: "Arrossega el vídeo aquí"
                    font.pixelSize: 18
                    palette.buttonText: parent.parent.containsDrag ? "#d4365b" : "#e9456c"
                    background: Item {}
                    Layout.alignment: Qt.AlignHCenter
                    hoverEnabled: false
                }

                Button {
                    text: "o seleccionar fitxer..."
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: inputDialog.open()
                    background: Rectangle {
                        color: parent.down ? "#969798" : (parent.hovered ? "#b9b9b9" : "#d7d7d5")
                        radius: 8
                        border.color: "#b9b9b9"
                        implicitWidth: 180
                        implicitHeight: 40
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#000000"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }

            // Loaded State (Left text, Right button)
            RowLayout {
                anchors.fill: parent
                anchors.margins: 15
                visible: videoPath !== ""
                spacing: 20

                Text {
                    text: videoPath !== "" ? "<b>" + videoPath.substring(videoPath.lastIndexOf("/") + 1) + "</b>" + (videoInfo !== "" ? ' &nbsp;&nbsp;&nbsp;&nbsp; <font color="#969798">' + videoInfo + '</font>' : "") : ""
                    color: "#000000"
                    textFormat: Text.StyledText
                    font.pixelSize: 14
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                    verticalAlignment: Text.AlignVCenter
                }

                Button {
                    text: "Canviar vídeo..."
                    Layout.alignment: Qt.AlignVCenter
                    onClicked: inputDialog.open()
                    background: Rectangle {
                        color: parent.down ? "#969798" : (parent.hovered ? "#b9b9b9" : "#d7d7d5")
                        radius: 8
                        border.color: "#b9b9b9"
                        implicitWidth: 140
                        implicitHeight: 36
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#000000"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                }
            }
        }
    }

    FileDialog {
        id: inputDialog
        title: "Selecciona un vídeo"
        nameFilters: ["Vídeos (*.mp4 *.mov *.mkv *.avi *.webm)"]
        onAccepted: videoPath = selectedFile
    }
}

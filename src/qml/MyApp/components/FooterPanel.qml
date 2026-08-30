import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Rectangle {
    Layout.fillWidth: true
    color: "#ffffff"
    radius: 12
    border.color: "#b9b9b9"
    border.width: 1
    implicitHeight: layout.implicitHeight + 40

    property bool canConvert: false
    property alias outputName: nameEntry.text
    property string outputDir: ""

    signal previewClicked
    signal convertClicked

    function setStatus(text, color) {
        statusText.text = text;
        if (color === "white" || color === "#000000") {
            statusText.color = "#969798";
        } else {
            statusText.color = color;
        }
    }

    function setProgress(percent) {
        progressBar.value = percent;
        progressLabel.text = Math.round(percent * 100) + "%";
    }

    ColumnLayout {
        id: layout
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        Text {
            text: "SORTIDA"
            color: "#969798"
            font.pixelSize: 12
            font.bold: true
            font.letterSpacing: 1
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 15

            Text {
                text: "Carpeta:"
                color: "#969798"
            }
            Button {
                text: "Canviar..."
                onClicked: outputDialog.open()
                background: Rectangle {
                    color: parent.down ? "#969798" : (parent.hovered ? "#b9b9b9" : "#d7d7d5")
                    radius: 8
                    border.color: "#b9b9b9"
                    border.width: 1
                    implicitHeight: 36
                    implicitWidth: 100
                }
                contentItem: Text {
                    text: parent.text
                    color: "#000000"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            Text {
                text: outputDir === "" ? "Carpeta" : outputDir.replace("file:///", "").split("/").join("\\")
                color: "#000000"
                Layout.fillWidth: true
                elide: Text.ElideMiddle
            }

            Text {
                text: "Nom:"
                color: "#969798"
            }
            TextField {
                id: nameEntry
                Layout.preferredWidth: 350
                color: "#000000"
                background: Rectangle {
                    color: "#d7d7d5"
                    radius: 8
                    border.color: "#b9b9b9"
                    border.width: 1
                }
                padding: 8
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#b9b9b9"
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 20

            ColumnLayout {
                Layout.fillWidth: true
                Text {
                    id: statusText
                    text: "Llest per generar"
                    color: "#969798"
                    font.pixelSize: 13
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }
                RowLayout {
                    Layout.fillWidth: true
                    ProgressBar {
                        id: progressBar
                        Layout.fillWidth: true
                        from: 0
                        to: 1.0
                        value: 0
                        background: Rectangle {
                            implicitHeight: 8
                            color: "#d7d7d5"
                            radius: 4
                        }
                        contentItem: Item {
                            implicitHeight: 8
                            Rectangle {
                                width: progressBar.visualPosition * parent.width
                                height: parent.height
                                radius: 4
                                color: "#e9456c"
                            }
                        }
                    }
                    Text {
                        id: progressLabel
                        text: "0%"
                        color: "#000000"
                        font.bold: true
                        Layout.minimumWidth: 40
                        horizontalAlignment: Text.AlignRight
                    }
                }
            }
                RowLayout {
                    spacing: 10
                    
                    Button {
                        text: "Previsualitzar"
                        enabled: canConvert
                        onClicked: previewClicked()
                        Layout.preferredHeight: 45
                        Layout.preferredWidth: 150
                        background: Rectangle {
                            color: parent.enabled ? (parent.down ? "#d7d7d5" : (parent.hovered ? "#f0f0f0" : "#ffffff")) : "#d7d7d5"
                            radius: 8
                            border.color: parent.enabled ? "#e9456c" : "#b9b9b9"
                            border.width: 2
                        }
                        contentItem: Text {
                            text: parent.text
                            color: parent.enabled ? "#e9456c" : "#b9b9b9"
                            font.bold: true
                            font.pixelSize: 16
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }

                    Button {
                        text: "Generar"
                        enabled: canConvert
                        onClicked: convertClicked()
                        Layout.preferredHeight: 45
                        Layout.preferredWidth: 150
                        background: Rectangle {
                            color: parent.enabled ? (parent.down ? "#be2649" : (parent.hovered ? "#d4365b" : "#e9456c")) : "#d7d7d5"
                            radius: 8
                        }
                        contentItem: Text {
                            text: parent.text
                            color: parent.enabled ? "#ffffff" : "#b9b9b9"
                            font.bold: true
                            font.pixelSize: 16
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
        }
    }

    FolderDialog {
        id: outputDialog
        title: "Selecciona carpeta de sortida"
        onAccepted: outputDir = selectedFolder
    }
}

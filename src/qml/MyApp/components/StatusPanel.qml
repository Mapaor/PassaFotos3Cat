import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    Layout.fillWidth: true
    color: "#ffffff"
    radius: 12
    border.color: "#b9b9b9"
    border.width: 1
    implicitHeight: 70
    
    function setStatus(text, color) {
        statusText.text = text
        // If they send white, use our secondary color instead for better look
        if (color === "white" || color === "#000000") {
            statusText.color = "#969798"
        } else {
            statusText.color = color
        }
    }
    
    function setProgress(percent) {
        progressBar.value = percent
        progressLabel.text = Math.round(percent * 100) + "%"
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 15
        spacing: 20
        
        Text {
            id: statusText
            text: "Selecciona un vídeo i clica 'Convertir'"
            color: "#969798"
            font.pixelSize: 13
            Layout.minimumWidth: 250
            elide: Text.ElideRight
        }
        
        ProgressBar {
            id: progressBar
            Layout.fillWidth: true
            from: 0; to: 1.0; value: 0
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
                    color: "#e9456c" // success green for progress
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

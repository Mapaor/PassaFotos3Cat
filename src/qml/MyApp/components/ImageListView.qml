import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Rectangle {
    id: root
    color: "#ffffff"
    radius: 12
    border.color: "#b9b9b9"
    border.width: 1
    implicitHeight: 140

    property alias model: listView.model
    property int currentIndex: listView.currentIndex

    signal addClicked()
    signal removeClicked(int index)
    signal editClicked(int index)
    signal filesDropped(var urls)

    DropArea {
        id: dropArea
        anchors.fill: parent
        
        Rectangle {
            anchors.fill: parent
            color: "#1Ae9456c"
            border.color: "#e9456c"
            border.width: 4
            visible: dropArea.containsDrag
            radius: 12
        }

        onEntered: function(drag) {
            if (drag.hasUrls) {
                drag.accept()
            } else {
                drag.ignore()
            }
        }
        onDropped: function(drop) {
            if (drop.hasUrls) {
                root.filesDropped(drop.urls)
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        Button {
            text: "+"
            font.pixelSize: 32
            Layout.preferredWidth: 60
            Layout.fillHeight: true
            onClicked: addClicked()
            background: Rectangle {
                color: parent.down ? "#be2649" : (parent.hovered ? "#d4365b" : "#e9456c")
                radius: 8
                border.color: "white"
                border.width: 2
            }
            contentItem: Text {
                text: parent.text
                color: "white"
                font.pixelSize: 32
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        ListView {
            id: listView
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: ListView.Horizontal
            spacing: 10
            clip: true

            delegate: Item {
                width: 160
                height: listView.height

                Rectangle {
                    anchors.fill: parent
                    color: listView.currentIndex === index ? "#fce4ec" : "transparent"
                    border.color: listView.currentIndex === index ? "#d4365b" : "#b9b9b9"
                    border.width: listView.currentIndex === index ? 3 : 1
                    radius: 8

                    Image {
                        anchors.fill: parent
                        anchors.margins: 4
                        source: path
                        fillMode: Image.PreserveAspectCrop
                        clip: true
                        sourceSize: Qt.size(160, 90)
                    }

                    HoverHandler {
                        id: hoverHandler
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            listView.currentIndex = index
                            root.editClicked(index)
                        }
                    }

                    Button {
                        opacity: hoverHandler.hovered ? 1.0 : 0.0
                        visible: opacity > 0
                        Behavior on opacity { NumberAnimation { duration: 150 } }
                        text: "X"
                        width: 28
                        height: 28
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.margins: 4
                        onClicked: root.removeClicked(index)
                        background: Rectangle {
                            color: parent.down ? "#99000000" : (parent.hovered ? "#cc000000" : "#66000000")
                            radius: 14
                        }
                        contentItem: Image {
                            source: "../assets/delete.svg"
                            sourceSize: Qt.size(20, 20)
                            fillMode: Image.PreserveAspectFit
                            horizontalAlignment: Image.AlignHCenter
                            verticalAlignment: Image.AlignVCenter
                        }
                    }
                    
                    Row {
                        anchors.bottom: parent.bottom
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottomMargin: 8
                        spacing: 8
                        opacity: hoverHandler.hovered ? 1.0 : 0.0
                        visible: opacity > 0
                        Behavior on opacity { NumberAnimation { duration: 150 } }
                        
                        Button {
                            width: 28
                            height: 28
                            enabled: index > 0
                            onClicked: root.model.move(index, index - 1, 1)
                            background: Rectangle {
                                color: parent.down ? "#99000000" : (parent.hovered ? "#cc000000" : "#66000000")
                                radius: 14
                            }
                            contentItem: Image {
                                source: "../assets/angle-left.svg"
                                sourceSize: Qt.size(16, 16)
                                fillMode: Image.PreserveAspectFit
                                horizontalAlignment: Image.AlignHCenter
                                verticalAlignment: Image.AlignVCenter
                                opacity: parent.enabled ? 1.0 : 0.5
                            }
                        }
                        Button {
                            width: 28
                            height: 28
                            enabled: index < root.model.count - 1
                            onClicked: root.model.move(index, index + 1, 1)
                            background: Rectangle {
                                color: parent.down ? "#99000000" : (parent.hovered ? "#cc000000" : "#66000000")
                                radius: 14
                            }
                            contentItem: Image {
                                source: "../assets/angle-right.svg"
                                sourceSize: Qt.size(16, 16)
                                fillMode: Image.PreserveAspectFit
                                horizontalAlignment: Image.AlignHCenter
                                verticalAlignment: Image.AlignVCenter
                                opacity: parent.enabled ? 1.0 : 0.5
                            }
                        }
                    }
                }
            }
        }
    }
}

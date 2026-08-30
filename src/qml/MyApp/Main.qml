import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtCore
import "components"

Window {
    id: mainWindow
    width: 900
    height: 700
    visible: true
    title: "PassaFotos3Cat"
    color: "#e0e0e0"

    property bool isConverting: false
    property bool hasImages: imagesModel.count > 0

    property string outputDir: footerPanel.outputDir
    property string outputName: footerPanel.outputName

    ListModel {
        id: imagesModel
        onCountChanged: {
            if (count > 0 && footerPanel.outputDir === "") {
                let firstPath = get(0).path.toString();
                if (firstPath.startsWith("file:///")) {
                    firstPath = firstPath.substring(8);
                }
                // Handle both Windows and Unix slashes
                let lastSlash = Math.max(firstPath.lastIndexOf("/"), firstPath.lastIndexOf("\\"));
                if (lastSlash !== -1) {
                    footerPanel.outputDir = "file:///" + firstPath.substring(0, lastSlash);
                    let filename = firstPath.substring(lastSlash + 1);
                    let dotIndex = filename.lastIndexOf(".");
                    if (dotIndex !== -1) {
                        filename = filename.substring(0, dotIndex);
                    }
                    footerPanel.outputName = "passafotos_" + filename + ".mp4";
                }
            } else if (count === 0) {
                footerPanel.outputDir = "";
                footerPanel.outputName = "";
            }
        }
    }

    FileDialog {
        id: fileDialog
        title: "Selecciona Imatges"
        currentFolder: StandardPaths.standardLocations(StandardPaths.PicturesLocation)[0]
        nameFilters: ["Imatges (*.png *.jpg *.jpeg *.webp)"]
        fileMode: FileDialog.OpenFiles
        onAccepted: {
            for (let i = 0; i < selectedFiles.length; i++) {
                imagesModel.append({
                    "path": selectedFiles[i],
                    "crop_x": 0.0,
                    "crop_y": 0.0,
                    "crop_w": 1.0,
                    "crop_h": 1.0,
                    "anchor_x": 0.5,
                    "anchor_y": 0.5
                });
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 15

        Text {
            text: "GENERADOR DE PASSAFOTOS"
            color: "#d4365b"
            font.pixelSize: 28
            font.bold: true
            font.family: "Segoe UI"
            Layout.alignment: Qt.AlignHCenter
            Layout.bottomMargin: 5
        }

        ImageListView {
            id: imageList
            Layout.fillWidth: true
            model: imagesModel
            onAddClicked: fileDialog.open()
            onRemoveClicked: function (index) {
                imagesModel.remove(index);
            }
            onEditClicked: function (index) {
                editorPanel.open();
            }
            onFilesDropped: function (urls) {
                for (let i = 0; i < urls.length; i++) {
                    let url = urls[i].toString();
                    let ext = url.substring(url.lastIndexOf('.')).toLowerCase();
                    if ([".png", ".jpg", ".jpeg", ".webp"].indexOf(ext) !== -1) {
                        imagesModel.append({
                            "path": urls[i],
                            "crop_x": 0.0,
                            "crop_y": 0.0,
                            "crop_w": 1.0,
                            "crop_h": 1.0,
                            "anchor_x": 0.5,
                            "anchor_y": 0.5
                        });
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Text {
                anchors.centerIn: parent
                text: hasImages ? "Clica una imatge per definir el seu punt d'ancoratge" : "Afegeix imatges per començar"
                color: "#969798"
                font.pixelSize: 18
                horizontalAlignment: Text.AlignHCenter
            }
        }

        ConfigPanel {
            id: configPanel
            Layout.fillWidth: true
        }

        FooterPanel {
            id: footerPanel
            Layout.fillWidth: true

            canConvert: hasImages && !mainWindow.isConverting

            onPreviewClicked: {
                footerPanel.setStatus("Generant preview ràpida...", "white");
                mainWindow.isConverting = true;
                footerPanel.setProgress(0);

                let data = [];
                for (let i = 0; i < imagesModel.count; i++) {
                    let item = imagesModel.get(i);
                    data.push({
                        "path": item.path,
                        "crop_x": item.crop_x,
                        "crop_y": item.crop_y,
                        "crop_w": item.crop_w,
                        "crop_h": item.crop_h,
                        "anchor_x": item.anchor_x,
                        "anchor_y": item.anchor_y
                    });
                }
                let jsonString = JSON.stringify(data);

                videoConverter.preview_slideshow(jsonString, configPanel.photoDuration, configPanel.transitionDuration, configPanel.zoomEnd);
            }

            onConvertClicked: {
                footerPanel.setStatus("Generant...", "white");
                mainWindow.isConverting = true;
                footerPanel.setProgress(0);

                // Serialize model data
                let data = [];
                for (let i = 0; i < imagesModel.count; i++) {
                    let item = imagesModel.get(i);
                    data.push({
                        "path": item.path,
                        "crop_x": item.crop_x,
                        "crop_y": item.crop_y,
                        "crop_w": item.crop_w,
                        "crop_h": item.crop_h,
                        "anchor_x": item.anchor_x,
                        "anchor_y": item.anchor_y
                    });
                }
                let jsonString = JSON.stringify(data);

                videoConverter.convert_slideshow(jsonString, mainWindow.outputDir, mainWindow.outputName, configPanel.photoDuration, configPanel.transitionDuration, configPanel.zoomEnd);
            }
        }
    }

    PreviewPanel {
        id: previewPanel
    }

    ImageEditorPanel {
        id: editorPanel

        property var currentItem: hasImages && imageList.currentIndex >= 0 && imageList.currentIndex < imagesModel.count ? imagesModel.get(imageList.currentIndex) : null

        imageSource: currentItem ? currentItem.path : ""
        cropX: currentItem ? currentItem.crop_x : 0.0
        cropY: currentItem ? currentItem.crop_y : 0.0
        cropW: currentItem ? currentItem.crop_w : 1.0
        cropH: currentItem ? currentItem.crop_h : 1.0
        anchorX: currentItem ? currentItem.anchor_x : 0.5
        anchorY: currentItem ? currentItem.anchor_y : 0.5

        onCropChanged: function (x, y, w, h) {
            if (currentItem) {
                imagesModel.setProperty(imageList.currentIndex, "crop_x", x);
                imagesModel.setProperty(imageList.currentIndex, "crop_y", y);
                imagesModel.setProperty(imageList.currentIndex, "crop_w", w);
                imagesModel.setProperty(imageList.currentIndex, "crop_h", h);
            }
        }

        onAnchorChanged: function (x, y) {
            if (currentItem) {
                imagesModel.setProperty(imageList.currentIndex, "anchor_x", x);
                imagesModel.setProperty(imageList.currentIndex, "anchor_y", y);
            }
        }
    }

    Connections {
        target: videoConverter

        function onProgressUpdated(percent) {
            footerPanel.setProgress(percent);
        }

        function onConversionFinished(success, message) {
            mainWindow.isConverting = false;
            footerPanel.setStatus(message, success ? "#7ef0b4" : "#be2649");
            if (success) {
                footerPanel.setProgress(1.0);
            } else {
                footerPanel.setProgress(0.0);
            }
        }

        function onPreviewFinished(success, message) {
            mainWindow.isConverting = false;
            if (success) {
                footerPanel.setStatus("Llest per generar", "white");
                footerPanel.setProgress(1.0);
                previewPanel.videoSource = message;
                previewPanel.open();
            } else {
                footerPanel.setStatus(message, "#be2649");
                footerPanel.setProgress(0.0);
            }
        }
    }
}

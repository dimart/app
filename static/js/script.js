function displayImages(response) {
    console.log("[displayImages]: Got response from the server.");
};

function clearWorkspace(response) {
    displayMessage("Thank you!", false);
};

// Create a local file input.
function createFileInput(button, callback) {
    var input = document.createElement('input');
    input.type = 'file';
    input.style.display = 'none';
    document.getElementsByTagName('body')[0].appendChild(input);

    input.addEventListener('change', function(event) {
        callback(event.target.files[0]);
    });

    button.addEventListener('click', function() {
        input.click();
    });
};

// Create a slide radio input.
function createToggleButton(button, disableCallback, enableCallback) {
    var enabled = true;
    button.addEventListener('click', function() {
        if (enabled) {
            disableCallback();
            button.classList.add('disabled');
        } else {
            enableCallback();
            button.classList.remove('disabled');
        }
        enabled = !enabled;
    });
}

// Create a legend.
function initializeLegend(annotator) {
    // Attach a click event to a legend item.
    function attachClickEvent(item, i) {
        item.addEventListener('click', function() {
            var selected = document.getElementsByClassName('legend-selected')[0];
            if (selected)
                selected.classList.remove('legend-selected');
            annotator.setCurrentLabel(i);
            this.classList.add('legend-selected');
        });
    }
    var labels = annotator.getLabels();

    var item = document.getElementById('sky-lab');
    attachClickEvent(item, 3);
    item = document.getElementById('vertical-lab');
    attachClickEvent(item, 2);
    item = document.getElementById('ground-lab');
    attachClickEvent(item, 1);

    document.getElementById('ground-lab').click();
};

// Attach button events
function initializeButtons(annotator) {
    var fillAlpha = 128;
    var boundaryEnabled = true;

    createToggleButton(document.getElementById('image-view'),
        function() {
            annotator.setImageAlpha(0);
        },
        function() {
            annotator.setImageAlpha(255);
        });

    createToggleButton(document.getElementById('boundary-view'),
        function() {
            annotator.setBoundaryAlpha(fillAlpha);
            boundaryEnabled = !boundaryEnabled;
        },
        function() {
            if (fillAlpha === 128)
                annotator.setBoundaryAlpha(192);
            boundaryEnabled = !boundaryEnabled;
        });

    createToggleButton(document.getElementById('fill-view'),
        function() {
            fillAlpha = 0;
            annotator.setFillAlpha(fillAlpha);
            annotator.setBoundaryAlpha(fillAlpha);
        },
        function() {
            fillAlpha = 128;
            annotator.setFillAlpha(fillAlpha);
            if (boundaryEnabled)
                annotator.setBoundaryAlpha(192);
            else
                annotator.setBoundaryAlpha(fillAlpha);
        });

    annotator.setImageAlpha(255);
}

function initSegmentAnnotator(segmentation) {
    options = {
        container: document.getElementById('annotator-container'),
        labels: [{
            name: 'background',
            color: [255, 255, 255]
        }, {
            name: 'ground',
            color: [0, 255, 0]
        }, {
            name: 'vertical',
            color: [255, 0, 0]
        }, {
            name: 'sky',
            color: [0, 0, 255]
        }],
        onload: function() {
            initializeLegend(this);
            initializeButtons(this);
            $("#loading").fadeOut("fast");
        }
    };
    SegmentAnnotator.call(Object.create(SegmentAnnotator.prototype), segmentation, options);
};

function displayMessage(withText, isItLoading) {
    $("#loading").fadeOut("fast");
    $("#loading").css({
        'left': '50%',
        'top': '50%',
        'margin-top': -$("#loading").height() / 2 - parseInt($("#loading").css('padding-top')),
        'margin-left': -$("#loading").width() / 2 - parseInt($("#loading").css('padding-left'))
    });
    console.log($("#loading").width());
    if (isItLoading) {
        $("#loading").html('<span><i class="fa fa-cog fa-spin"></i>&emsp;' + withText + '</span>');
    } else {
        $("#loading").html(withText);
    }
    $("#loading").fadeIn("fast");
};

window.onload = function() {
    // Set up image loader
    createFileInput(document.getElementById('label-image'), function(file) {
        if (file.type == 'image/jpeg' || file.type == 'image/png') {
            var formData = new FormData();
            formData.append('file', file);
            document.imageName = file.name;
            $.ajax({
                url: "/api/1.0/process_image",
                type: "POST",
                data: formData,
                success: initSegmentAnnotator,
                contentType: false,
                processData: false
            });
            displayMessage("Processing Image...", true);
        } else {
            alert("Unsupported image type.\n Try to load jpeg or png.");
        }
    });

    document.getElementById('brawse-images').onclick = function() {
        // $.ajax({
        //     url: "/api/1.0/get_images",
        //     type: "GET",
        //     success: displayImages
        // });

        displayMessage("Not available", false);
    };
};

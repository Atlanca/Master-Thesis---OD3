 d3.demo = {};

    /** CANVAS **/
    d3.demo.canvas = function() {

        "use strict";

        var width           = 7000,
            height          = 4200,
            zoomEnabled     = true,
            dragEnabled     = true,
            scale           = 1,
            translation     = [0,0],
            base            = null,
            wrapperBorder   = 0,
            minimap         = null,
            minimapPadding  = 0,
            minimapScale    = 200/3000;

        function canvas(selection) {

            base = selection;

            var xScale = d3.scale.linear()
                .domain([-width / 2, width / 2])
                .range([0, width]);

            var yScale = d3.scale.linear()
                .domain([-height / 2, height / 2])
                .range([height, 0]);

            var zoomHandler = function(newScale) {
                if (!zoomEnabled) { return; }
                if (d3.event) {
                    scale = d3.event.scale;
                } else {
                    scale = newScale;
                }
                if (dragEnabled) {
                    var tbound = -height * scale,
                        bbound = height  * scale,
                        lbound = -width  * scale,
                        rbound = width   * scale;
                    // limit translation to thresholds
                    translation = d3.event ? d3.event.translate : [0, 0];
                    translation = [
                        Math.max(Math.min(translation[0], rbound), lbound),
                        Math.max(Math.min(translation[1], bbound), tbound)
                    ];
                }

                d3.select(".panCanvas, .panCanvas .bg")
                    .attr("transform", "translate(" + translation + ")" + " scale(" + scale + ")");

                minimap.scale(scale).render();
            }; // startoff zoomed in a bit to show pan/zoom rectangle

            var zoom = d3.behavior.zoom()
                .x(xScale)
                .y(yScale)
                .scaleExtent([0.4, 3])
                .on("zoom.canvas", zoomHandler);

            var svg = selection.append("svg")
                .attr("class", "svg canvas")
                .attr("width",  width  + (wrapperBorder*2) + minimapPadding*2 + (width*minimapScale))
                .attr("height", height + (wrapperBorder*2) + minimapPadding*2)
                .attr("shape-rendering", "auto");

            var svgDefs = svg.append("defs");

            svgDefs.append("clipPath")
                .attr("id", "wrapperClipPath_qwpyza")
                .attr("class", "wrapper clipPath")
                .append("rect")
                .attr("class", "background")
                .attr("width", width)
                .attr("height", height);

            svgDefs.append("clipPath")
                .attr("id", "minimapClipPath_qwpyza")
                .attr("class", "minimap clipPath")
                .attr("width", width)
                .attr("height", height)
                //.attr("transform", "translate(" + (width + minimapPadding) + "," + (minimapPadding/2) + ")")
                .append("rect")
                .attr("class", "background")
                .attr("width", width)
                .attr("height", height);

            var filter = svgDefs.append("svg:filter")
                .attr("id", "minimapDropShadow_qwpyza")
                .attr("x", "-20%")
                .attr("y", "-20%")
                .attr("width", "150%")
                .attr("height", "150%");

            filter.append("svg:feOffset")
                .attr("result", "offOut")
                .attr("in", "SourceGraphic")
                .attr("dx", "1")
                .attr("dy", "1");

            filter.append("svg:feColorMatrix")
                .attr("result", "matrixOut")
                .attr("in", "offOut")
                .attr("type", "matrix")
                .attr("values", "0.1 0 0 0 0 0 0.1 0 0 0 0 0 0.1 0 0 0 0 0 0.5 0");

            filter.append("svg:feGaussianBlur")
                .attr("result", "blurOut")
                .attr("in", "matrixOut")
                .attr("stdDeviation", "10");

            filter.append("svg:feBlend")
                .attr("in", "SourceGraphic")
                .attr("in2", "blurOut")
                .attr("mode", "normal");

            var outerWrapper = svg.append("g")
                .attr("class", "wrapper outer")
                .attr("transform", "translate(0, " + minimapPadding + ")");

            outerWrapper.append("rect")
                .attr("class", "background")
                .attr("width", width + wrapperBorder*2)
                .attr("height", height + wrapperBorder*2);

            var innerWrapper = outerWrapper.append("g")
                .attr("class", "wrapper inner")
                .attr("clip-path", "url(#wrapperClipPath_qwpyza)")
                .attr("transform", "translate(" + (wrapperBorder) + "," + (wrapperBorder) + ")")
                .call(zoom);

            innerWrapper.append("rect")
                .attr("class", "background")
                .attr("width", width)
                .attr("height", height);

            var panCanvas = innerWrapper.append("g")
                .attr("class", "panCanvas")
                .attr("width", width)
                .attr("height", height)
                .attr("transform", "translate(0,0)");

            panCanvas.append("rect")
                .attr("class", "background")
                .attr("width", width)
                .attr("height", height);

            minimap = d3.demo.minimap()
                .zoom(zoom)
                .target(panCanvas)
                .minimapScale(minimapScale)
                // .x(width + minimapPadding)
                // .y(minimapPadding);

            svg.call(minimap);

            // startoff zoomed in a bit to show pan/zoom rectangle
            zoom.scale(1.75);
            zoomHandler(1.75);

            /** ADD SHAPE **/
            canvas.addItem = function(item) {
                panCanvas.node().appendChild(item.node());
                minimap.render();
            };

            /** RENDER **/
            canvas.render = function() {
                svgDefs
                    .select(".clipPath .background")
                    .attr("width", width)
                    .attr("height", height);

                svg
                    .attr("width",  width  + (wrapperBorder*2) + minimapPadding*2 + (width*minimapScale))
                    .attr("height", height + (wrapperBorder*2));

                outerWrapper
                    .select(".background")
                    .attr("width", width + wrapperBorder*2)
                    .attr("height", height + wrapperBorder*2);

                innerWrapper
                    .attr("transform", "translate(" + (wrapperBorder) + "," + (wrapperBorder) + ")")
                    .select(".background")
                    .attr("width", width)
                    .attr("height", height);

                panCanvas
                    .attr("width", width)
                    .attr("height", height)
                    .select(".background")
                    .attr("width", width)
                    .attr("height", height);

                minimap
                    .x(width + minimapPadding)
                    .y(minimapPadding)
                    .render();
            };

            canvas.zoomEnabled = function(isEnabled) {
                if (!arguments.length) { return zoomEnabled }
                zoomEnabled = isEnabled;
            };

            canvas.dragEnabled = function(isEnabled) {
                if (!arguments.length) { return dragEnabled }
                dragEnabled = isEnabled;
            };

            canvas.reset = function() {
                svg.call(zoom.event);
                zoom.scale(1);
                zoom.translate([0,0]);
                svg.transition().duration(750).call(zoom.event);
            };
        }


        //============================================================
        // Accessors
        //============================================================

        canvas.width = function(value) {
            if (!arguments.length) return width;
            width = parseInt(value, 10);
            return this;
        };

        canvas.height = function(value) {
            if (!arguments.length) return height;
            height = parseInt(value, 10);
            return this;
        };

        canvas.scale = function(value) {
            if (!arguments.length) { return scale; }
            scale = value;
            return this;
        };

        return canvas;
    };



    /** MINIMAP **/
    d3.demo.minimap = function() {

        "use strict";

        var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
        var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0) 

        var minimapScale    = 0,
            scale           = 1,
            zoom            = null,
            base            = null,
            target          = null,
            width           = 200,
            height          = 200,
            frameWidth      = w,
            frameHeight     = h,
            x               = 10
            ,
            y               = 500,
            frameX          = 0,
            frameY          = 0;

        function minimap(selection) {

            base = selection;

            var container = selection.append("g")
                .attr("class", "minimap")
                .call(zoom);

            zoom.on("zoom.minimap", function() {
                scale = d3.event.scale;
            });


            minimap.node = container.node();

            var frame = container.append("g")
                .attr("class", "frame")

            frame.append("rect")
                .attr("class", "background")
                .attr("width", frameWidth)
                .attr("height", frameHeight)
                .attr("filter", "url(#minimapDropShadow_qwpyza)");

            var drag = d3.behavior.drag()
                .on("dragstart.minimap", function() {
                    var frameTranslate = d3.demo.util.getXYFromTranslate(frame.attr("transform"));
                    frameX = frameTranslate[0];
                    frameY = frameTranslate[1];
                })
                .on("drag.minimap", function() {
                    d3.event.sourceEvent.stopImmediatePropagation();
                    frameX += d3.event.dx;
                    frameY += d3.event.dy;
                    frame.attr("transform", "translate(" + frameX + "," + frameY + ")");
                    var translate =  [(-frameX*scale),(-frameY*scale)];
                    target.attr("transform", "translate(" + translate + ")scale(" + scale + ")");
                    zoom.translate(translate);
                });

            frame.call(drag);

            /** RENDER **/
            minimap.render = function() {
                scale = zoom.scale();
                container.attr("transform", "translate(" + x + "," + y + ")scale(" + minimapScale + ")");
                var node = target.node().cloneNode(true);
                node.removeAttribute("id");
                base.selectAll(".minimap .panCanvas").remove();
                minimap.node.appendChild(node);
                var targetTransform = d3.demo.util.getXYFromTranslate(target.attr("transform"));
                frame.attr("transform", "translate(" + (-targetTransform[0]/scale) + "," + (-targetTransform[1]/scale) + ")")
                    .select(".background")
                    .attr("width", frameWidth/scale)
                    .attr("height", frameHeight/scale)
                frame.node().parentNode.appendChild(frame.node());
                d3.select(node).attr("transform", "translate(1,1)");
            };
        }


        //============================================================
        // Accessors
        //============================================================


        minimap.width = function(value) {
            if (!arguments.length) return width;
            width = parseInt(value, 10);
            return this;
        };


        minimap.height = function(value) {
            if (!arguments.length) return height;
            height = parseInt(value, 10);
            return this;
        };


        minimap.x = function(value) {
            if (!arguments.length) return x;
            x = parseInt(value, 10);
            return this;
        };


        minimap.y = function(value) {
            if (!arguments.length) return y;
            y = parseInt(value, 10);
            return this;
        };


        minimap.scale = function(value) {
            if (!arguments.length) { return scale; }
            scale = value;
            return this;
        };


        minimap.minimapScale = function(value) {
            if (!arguments.length) { return minimapScale; }
            minimapScale = value;
            return this;
        };


        minimap.zoom = function(value) {
            if (!arguments.length) return zoom;
            zoom = value;
            return this;
        };


        minimap.target = function(value) {
            if (!arguments.length) { return target; }
            target = value;
            width  = parseInt(target.attr("width"),  10);
            height = parseInt(target.attr("height"), 10);
            return this;
        };

        return minimap;
    };


    /** UTILS **/
    d3.demo.util = {};
    d3.demo.util.getXYFromTranslate = function(translateString) {
        var currentTransform = d3.transform(translateString);
        currentX = currentTransform.translate[0];
        currentY = currentTransform.translate[1];
        return [currentX, currentY];
    };


    /** RUN SCRIPT **/
    var canvasWidth = 800;
    var shapes = [];
    var lastXY = 1;
    var zoomEnabled = true;
    var dragEnabled = true;

    var canvas = d3.demo.canvas();
    d3.select("#canvasQwpYZa").call(canvas);

    function addItem(item) {
        canvas.addItem(d3.select(item));
        canvas.reset()
    }

    var jointViewport = d3.select('.joint-viewport')
    console.log(d3.selectAll('rect'))
    d3.selectAll('.joint-cell rect').on('click', function(){
        console.log('watt')
    })

    
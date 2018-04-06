// Create the input graph
var g = new dagreD3.graphlib.Graph().setGraph({rankdir: "RL"})
  .setDefaultEdgeLabel(function() { return {}; });

// Here we"re setting nodeclass, which is used by our custom drawNodes function
// below.
var i = 1;
var states = {
  "Features": {
    id: "node_Features",
    class: "box",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request.",
    style: "fill: #70b8ff"
  },
  "purchase_products": {
    id: "node_purchase_products",
    title: "represents no connection state at all."
  },

  "Requirements": {
    id: "node_requirements",
    title: "represents waiting for a connection request from any " +
                 "remote TCP and port.",
    style: "fill: #70b8ff"
  },
  "add_item_to_cart": {
    id: "node_add_item_to_cart",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request."
  },
  "update_item_in_cart": {
    id: "node_update_item_in_cart",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request."
  },
  "mini_cart": {
    id: "node_mini_cart",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request."
  },
  "payment": {
    id: "node_payment",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request."
  },
  "place_order": {
    id: "node_place_order",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request."
  },
  "list_orders": {
    id: "node_list_orders",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request."
  },
  "remove_item_from_cart": {
    id: "node_remove_item_from_cart",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request."
  },

  "Use cases": {
    id: "node_use_cases",
    title: "represents waiting for a matching connection " +
                 "request after having sent a connection request.",
    style: "fill: #70b8ff"
  },
  "browse_catalog": {
    id: "node_browse_catalog",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request."
  },

  "Diagrams": {
    id: "node_diagrams",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request.",
    style: "fill: #70b8ff"
  },
  "figure_3.4_purchase_products": {
    id: "node_figure_3.4_purchase_products",
    title: "represents waiting for a confirming connection " +
                 "request acknowledgment after having both received and sent a " +
                 "connection request."
  },
};

// Add states to the graph, set labels, and style
Object.keys(states).forEach(function(state) {
  var value = states[state];
  value.label = state;
  value.rx = value.ry = 5;
  g.setNode(state, value);
  console.log(value)
});

// Set up the edges
g.setEdge("purchase_products", "Features", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})

g.setEdge("Requirements", "purchase_products", {curve: d3.curveBasis})
g.setEdge("add_item_to_cart", "Requirements", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})
g.setEdge("update_item_in_cart", "Requirements", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})
g.setEdge("mini_cart", "Requirements", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})
g.setEdge("list_orders", "Requirements", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})
g.setEdge("payment", "Requirements", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})
g.setEdge("place_order", "Requirements", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})
g.setEdge("remove_item_from_cart", "Requirements", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})

g.setEdge("Use cases", "purchase_products", {curve: d3.curveBasis})
g.setEdge("browse_catalog", "Use cases", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})

g.setEdge("Diagrams", "purchase_products", {curve: d3.curveBasis})
g.setEdge("figure_3.4_purchase_products", "Diagrams", {curve: d3.curveBasis, arrowheadStyle: 'fill: #fff'})

// Create the renderer
var render = new dagreD3.render();

// Set up an SVG group so that we can translate the final graph.
var svg = d3.select("svg"),
    inner = svg.append("g");

// Set up zoom support
var zoom = d3.zoom()
    .on("zoom", function() {
      inner.attr("transform", d3.event.transform);
    });
svg.call(zoom);

// Run the renderer. This is what draws the final graph.
render(inner, g);

// Center the graph
var initialScale = 0.75;
svg.call(zoom.transform, d3.zoomIdentity.translate((svg.attr("width") - g.graph().width * initialScale) / 2, 20).scale(initialScale));

for(var element in states) {
  node = document.getElementById(states[element]['id']).setAttribute('title', "<p>" + element + "</p>" + "<p>" + states[element]['title'] + "</p>")
  console.log(node)
}


tippy('.node')

svg.selectAll("g.node").on("click", function(id){
  document.getElementById(id).scrollIntoView();
});

svg.attr('height', g.graph().height * initialScale + 40);
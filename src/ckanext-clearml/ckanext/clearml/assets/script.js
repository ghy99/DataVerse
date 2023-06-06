// Assume your graph data is stored in a variable called 'graphData'
const graphData = {
    '469679a1bcfa4315a0abe709edc359ba': [],
    '971eb409df69416a83b3ef4a3f82eb93': ['469679a1bcfa4315a0abe709edc359ba'],
    '34155a2333e7477c8870fa7e31166f3f': ['971eb409df69416a83b3ef4a3f82eb93'],
    '9f3c535b2d8b45988ebee95850e7c5e1': ['971eb409df69416a83b3ef4a3f82eb93'],
    '059bb2f1476f47f6b15fcb1081d190c9': ['9f3c535b2d8b45988ebee95850e7c5e1', '34155a2333e7477c8870fa7e31166f3f'],
};

// Select the graph container element
const container = d3.select("#graph-container");

// Set the dimensions of the SVG container
const width = container.node().getBoundingClientRect().width;
const height = 400;

// Create a new SVG element within the container
const svg = container.append("svg")
    .attr("width", width)
    .attr("height", height);

// Extract the unique nodes from the graphData
const nodesSet = new Set(Object.keys(graphData));
Object.values(graphData).forEach(parents => {
    parents.forEach(parent => {
        nodesSet.add(parent);
    });
});

console.log("Nodes Set: ", nodesSet)

// Create an array of node objects with initial x and y positions
const nodes = Array.from(nodesSet).map((node, index) => ({
    id: node,
    x: (index / (nodesSet.size - 1)) * width, // Position the nodes along the x-axis
    y: height * nodesSet.size - 1, // Place the nodes vertically at the center
  }));

// Create an array of link objects
const links = [];
Object.entries(graphData).forEach(([child, parents]) => {
    parents.forEach(parent => {
        const source = nodes.find(node => node.id === parent);
        const target = nodes.find(node => node.id === child);
        links.push({ source, target });
    });
});

// Create D3.js force simulation to position the nodes
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(200))
    .force("charge", d3.forceManyBody().strength(-100))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide(50));

// Create SVG elements for the links
const link = svg.selectAll(".link")
    .data(links)
    .enter()
    .append("line")
    .attr("class", "link")
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y)
    .style("stroke", "black");


// Create SVG elements for the nodes
const node = svg.selectAll(".node")
  .data(nodes)
  .enter()
  .append("g")
  .attr("class", "node");

// Append circles to the node elements
node.append("circle")
  .attr("r", 10);

// Append text labels to the node elements
node.append("text")
  .attr("dx", -120) // Adjust the x-offset of the text label
  .attr("dy", 20) // Adjust the y-offset of the text label
  .text(d => d.id); // Set the label text

// Update the node positions in the simulation
simulation.on("tick", () => {
  node.attr("transform", d => `translate(${d.x},${d.y})`);
  link.attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
});

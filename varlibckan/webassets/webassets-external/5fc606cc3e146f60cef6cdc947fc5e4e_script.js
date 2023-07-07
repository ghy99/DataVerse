ckan.module("versiontree-module", function ($, _) {
  "use strict";
  return {
    options: {
      debug: false,
    },

    initialize: function () {},
  };
});

function renderTree(graphData, dataset_IDs, dataset_details) {
  console.log(dataset_IDs)
  console.log(graphData)
  console.log(dataset_details)
  // Assume your graph data is stored in a variable called 'graphData'
  // const graphData = {
  //     '469679a1bcfa4315a0abe709edc359ba': [],
  //     '971eb409df69416a83b3ef4a3f82eb93': ['469679a1bcfa4315a0abe709edc359ba'],
  //     '34155a2333e7477c8870fa7e31166f3f': ['971eb409df69416a83b3ef4a3f82eb93'],
  //     '9f3c535b2d8b45988ebee95850e7c5e1': ['971eb409df69416a83b3ef4a3f82eb93'],
  //     '059bb2f1476f47f6b15fcb1081d190c9': ['9f3c535b2d8b45988ebee95850e7c5e1', '34155a2333e7477c8870fa7e31166f3f'],
  // };

  // Select the graph container element
  const container = d3.select("#graph-container");

  // Set the dimensions of the SVG container
  const width = container.node().getBoundingClientRect().width;
  const height = container.node().getBoundingClientRect().height;

  // Create a new SVG element within the container
  const svg = container.append("svg")
      .attr("width", width)
      .attr("height", height);

  // Extract the unique nodes from the graphData
  // const nodesSet = new Set(Object.keys(graphData));
  // Object.values(graphData).forEach(parents => {
  //     parents.forEach(parent => {
  //         nodesSet.add(parent);
  //     });
  // });

  // console.log("Nodes Set: ", nodesSet);
  const nodesSet = new Set();
  dataset_IDs.forEach(key => {
      nodesSet.add(key);
      if (graphData.hasOwnProperty(key)) {
          graphData[key].forEach(parent => {
              nodesSet.add(parent);
          });
      }
  });

  console.log(nodesSet);

  // Create an array of node objects with initial x and y positions
  const nodes = Array.from(nodesSet).map((node, index) => ({
      id: node,
      x: height / 2, // Place the nodes vertically at the cente
      y: (index / (nodesSet.size - 1)) * width, // rPosition the nodes along the x-axis
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
      .force("collide", d3.forceCollide(100));

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
  .attr("dy", 30) // Adjust the y-offset of the text label
  .html(d => {
      const id = d.id;
      const version = dataset_details[d.id]['version'];
      const project = dataset_details[d.id]['project'];
      const name = dataset_details[d.id]['name'];
      const description = dataset_details[d.id]['description'];
      return `
      <tspan x="0" dy="1.2em">${project}</tspan>
      <tspan x="0" dy="1.2em">${name}</tspan>
      <tspan x="0" dy="1.2em">${version}</tspan>
      <tspan x="0" dy="1.2em">${description}</tspan>
      `;
  });

  // Update the node positions in the simulation
  simulation.on("tick", () => {
      node.attr("transform", d => `translate(${d.x},${d.y})`);
      link.attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);
  });
}
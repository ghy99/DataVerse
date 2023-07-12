function get_nodes_set(dataset_IDs, graphData) {
    const nodesSet = new Set();
    dataset_IDs.forEach(key => {
        nodesSet.add(key);
        if (graphData.hasOwnProperty(key)) {
            graphData[key].forEach(parent => {
                nodesSet.add(parent);
            });
        }
    });

    return nodesSet;
}

function get_nodes(nodesSet, height, width) {
    const nodes = Array.from(nodesSet).map((node, index) => ({
        id: node,
        x: height / 2, // Place the nodes vertically at the cente
        y: ((index + 1) / (nodesSet.size)) * (width - 100) + 200, // rPosition the nodes along the x-axis
    }));

    return nodes;
}

function get_links(graphData, nodes) {
    const links = [];
    Object.entries(graphData).forEach(([child, parents]) => {
        parents.forEach(parent => {
            const source = nodes.find(node => node.id === parent);
            const target = nodes.find(node => node.id === child);
            links.push({ source, target });
        });
    });

    return links;
}

function get_simulation(nodes, links, height, width) {
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(150))
        .force("charge", d3.forceManyBody().strength(-50))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collide", d3.forceCollide(50));

    return simulation;
}

function create_svg_for_links(svg, links) {
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

    return link;
}

function create_svg_for_nodes(svg, nodes) {
    const node = svg.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node");

    return node;
}

function get_node_container(dataset_details, node) {
    const nodeContainer = node.append("g");

    nodeContainer
        .append("rect")
        .attr("class", "node-box")
        .attr("x", 10)  // Adjust the x position of the rectangle
        .attr("y", -40) // Adjust the y position of the rectangle
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("width", 200)
        .attr("height", 80);

    // Append the text inside the rectangle box
    nodeContainer
        .append("text")
        .attr("class", "node-text")
        .attr("x", 110)  // Adjust the x position of the text
        .attr("y", -30)   // Adjust the y position of the text
        .attr("text-anchor", "start") // Align the text to the start of the box
        .selectAll("tspan")
        .data(d => {
            const id = d.id;
            const version = "Version: " + dataset_details[d.id]["version"];
            const project = "Project Title: " + dataset_details[d.id]["project"];
            const name = "Dataset Name: " + dataset_details[d.id]["name"];
            // const description = dataset_details[d.id]["description"];
            return [project, name, version];
        })
        .enter()
        .append("tspan")
        .attr("x", 110)  // Adjust the x position of the tspan
        .attr("dy", "1.2em")
        .text(d => d)
        .call(wrapText, 200, 1);

    function wrapText(text, width, lineHeight) {
        text.each(function () {
            var text = d3.select(this),
                words = text.text().split(/\s+/).reverse(),
                word,
                line = [],
                lineNumber = 0,
                lineHeight = lineHeight || 1, // Set the default line height if not provided
                y = text.attr("y"),
                dy = parseFloat(text.attr("dy")),
                tspan = text.text(null)
                    .append("tspan")
                    .attr("x", 110)
                    .attr("y", y)
                    .attr("dy", dy + "em");

            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(" "));

                if (tspan.node().getComputedTextLength() > width) {
                    line.pop();
                    tspan.text(line.join(" "));
                    line = [word];
                    tspan = text.append("tspan")
                        .attr("x", 110)
                        .attr("y", y)
                        .attr("dy", dy + "em")
                        .text(word);
                }
            }
        });
    }

    return nodeContainer;
}


function debug(graphData, dataset_IDs, dataset_details) {
    const container = d3.select("#graph-container");

    const width = container.node().getBoundingClientRect().width - 20;
    const height = container.node().getBoundingClientRect().height - 20;
    console.log("width: " + width + " ----- height: " + height);
    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("overflow", "hidden"); // Prevent content from overflowing the SVG

    const nodesSet = get_nodes_set(dataset_IDs, graphData);
    console.log("nodesSet: ", nodesSet);

    // Create an array of node objects with initial x and y positions
    const nodes = get_nodes(nodesSet, height, width);
    console.log("nodes: ", nodes);

    const links = get_links(graphData, nodes);
    console.log("links: ", links);

    const simulation = get_simulation(nodes, links, height, width);
    console.log("simulation: ", simulation);

    const link = create_svg_for_links(svg, links);
    console.log("link: ", link);

    const node = create_svg_for_nodes(svg, nodes);
    console.log("node: ", node);

    node.append("circle")
        .attr("r", 10)
        .on("mouseover", function () {
            d3.select(this).select(".node-box").style("opacity", 1);
            d3.select(this).select(".node-text").style("opacity", 1);
        })
        .on("mouseout", function () {
            d3.select(this).select(".node-box").style("opacity", 0);
            d3.select(this).select(".node-text").style("opacity", 0);
        });

    // Append the group container for each node
    const nodeContainer = get_node_container(dataset_details, node);

    simulation.on("tick", () => {
        node.attr("transform", d => `translate(${clamp(d.x, 0, width)},${clamp(d.y, 0, height)})`);
        link.attr("x1", d => clamp(d.source.x, 0, width))
            .attr("y1", d => clamp(d.source.y, 0, height))
            .attr("x2", d => clamp(d.target.x, 0, width))
            .attr("y2", d => clamp(d.target.y, 0, height));
    });

    // Clamp function to restrict the position within the container bounds
    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }
}

function renderTree(graphData, dataset_IDs, dataset_details) {
    console.log("graph data: ", graphData)
    console.log("dataset_IDs: ", dataset_IDs)
    console.log("dataset_details: ", dataset_details)
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

    const svg = container.append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("overflow", "hidden"); // Prevent content from overflowing the SVG

    // Create a new SVG element within the container
    // const svg = container.append("svg")
    //     .attr("width", width)
    //     .attr("height", height);

    // Extract the unique nodes from the graphData
    // const nodesSet = new Set(Object.keys(graphData));
    // Object.values(graphData).forEach(parents => {
    //     parents.forEach(parent => {
    //         nodesSet.add(parent);
    //     });
    // });

    // console.log("Nodes Set: ", nodesSet);
    const nodesSet = get_nodes_set(dataset_IDs, graphData);
    console.log("nodesSet: ", nodesSet);

    // Create an array of node objects with initial x and y positions
    const nodes = get_nodes(nodesSet, height, width);
    console.log("nodes: ", nodes);

    const links = get_links(graphData, nodes);
    console.log("links: ", links);

    const simulation = get_simulation(nodes, links, height, width);
    console.log("simulation: ", simulation);

    // Create SVG elements for the links
    const link = create_svg_for_links(links);
    console.log("link: ", link);

    // Create SVG elements for the nodes
    const node = create_svg_for_nodes(nodes);
    console.log("node: ", node);

    // Append circles to the node elements
    node.append("circle")
        .attr("r", 10)
        .on("mouseover", function () {
            d3.select(this).select(".node-box").style("opacity", 1);
            d3.select(this).select(".node-text").style("opacity", 1);
        })
        .on("mouseout", function () {
            d3.select(this).select(".node-box").style("opacity", 0);
            d3.select(this).select(".node-text").style("opacity", 0);
        });

    // Append the group container for each node
    const nodeContainer = node.append("g");

    // Append the rectangle box for each node
    // nodeContainer
    //     .append("rect")
    //     .attr("class", "node-box")
    //     .attr("x", -90)
    //     .attr("y", -90)
    //     .attr("rx", 5)
    //     .attr("ry", 5)
    //     .attr("width", 180)
    //     .attr("height", 80);

    // // Append the text inside the rectangle box
    // nodeContainer
    //     .append("text")
    //     .attr("class", "node-text")
    //     .attr("x", 0)
    //     .attr("y", -90)
    //     .attr("text-anchor", "middle")
    //     .selectAll("tspan")
    //     .data(d => {
    //         const id = d.id;
    //         const version = "Version: " + dataset_details[d.id]["version"];
    //         const project = "Project Title: " + dataset_details[d.id]["project"];
    //         const name = "Dataset Name: " + dataset_details[d.id]["name"];
    //         // const description = dataset_details[d.id]["description"];
    //         return [project, name, version];
    //     })
    //     .enter()
    //     .append("tspan")
    //     .attr("x", 0)
    //     .attr("dy", "1.2em")
    //     .text(d => d)
    //     .call(wrapText, 150, 1);

    // Append the rectangle box for each node
    nodeContainer
        .append("rect")
        .attr("class", "node-box")
        .attr("x", 10)  // Adjust the x position of the rectangle
        .attr("y", -40) // Adjust the y position of the rectangle
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("width", 200)
        .attr("height", 80);

    // Append the text inside the rectangle box
    nodeContainer
        .append("text")
        .attr("class", "node-text")
        .attr("x", 110)  // Adjust the x position of the text
        .attr("y", -30)   // Adjust the y position of the text
        .attr("text-anchor", "start") // Align the text to the start of the box
        .selectAll("tspan")
        .data(d => {
            const id = d.id;
            const version = "Version: " + dataset_details[d.id]["version"];
            const project = "Project Title: " + dataset_details[d.id]["project"];
            const name = "Dataset Name: " + dataset_details[d.id]["name"];
            // const description = dataset_details[d.id]["description"];
            return [project, name, version];
        })
        .enter()
        .append("tspan")
        .attr("x", 110)  // Adjust the x position of the tspan
        .attr("dy", "1.2em")
        .text(d => d)
        .call(wrapText, 200, 1);

    function wrapText(text, width, lineHeight) {
        text.each(function () {
            var text = d3.select(this),
                words = text.text().split(/\s+/).reverse(),
                word,
                line = [],
                lineNumber = 0,
                lineHeight = lineHeight || 1, // Set the default line height if not provided
                y = text.attr("y"),
                dy = parseFloat(text.attr("dy")),
                tspan = text.text(null)
                    .append("tspan")
                    .attr("x", 110)
                    .attr("y", y)
                    .attr("dy", dy + "em");

            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(" "));

                if (tspan.node().getComputedTextLength() > width) {
                    line.pop();
                    tspan.text(line.join(" "));
                    line = [word];
                    tspan = text.append("tspan")
                        .attr("x", 110)
                        .attr("y", y)
                        .attr("dy", dy + "em")
                        .text(word);
                }
            }
        });
    }
    // Append text labels to the node elements
    // node.append("text")
    //     .attr("dx", -120) // Adjust the x-offset of the text label
    //     .attr("dy", 30) // Adjust the y-offset of the text label
    //     .html(d => {
    //         const id = d.id;
    //         const version = dataset_details[d.id]['version'];
    //         const project = dataset_details[d.id]['project'];
    //         const name = dataset_details[d.id]['name'];
    //         const description = dataset_details[d.id]['description'];
    //         return `
    //   <tspan x="0" dy="1.2em">${project}</tspan>
    //   <tspan x="0" dy="1.2em">${name}</tspan>
    //   <tspan x="0" dy="1.2em">${version}</tspan>
    //   <tspan x="0" dy="1.2em">${description}</tspan>
    //   `;
    //     });

    // Update the node positions in the simulation
    // simulation.on("tick", () => {
    //     node.attr("transform", d => `translate(${d.x},${d.y})`);
    //     link.attr("x1", d => d.source.x)
    //         .attr("y1", d => d.source.y)
    //         .attr("x2", d => d.target.x)
    //         .attr("y2", d => d.target.y);
    // });

    simulation.on("tick", () => {
        node.attr("transform", d => `translate(${clamp(d.x, 0, width)},${clamp(d.y, 0, height)})`);
        link.attr("x1", d => clamp(d.source.x, 0, width))
            .attr("y1", d => clamp(d.source.y, 0, height))
            .attr("x2", d => clamp(d.target.x, 0, width))
            .attr("y2", d => clamp(d.target.y, 0, height));
    });

    console.log("after simulation")

    // Clamp function to restrict the position within the container bounds
    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }
}
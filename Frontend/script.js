const BASE_PATH = "http://localhost:3000"

async function fetchText(pathname) {
    const response = await fetch(new URL(`/api/${pathname}`, BASE_PATH));
    return await response.text();
}

async function fetchJSON(pathname) {
    const response = await fetch(new URL(`/api/${pathname}`, BASE_PATH));
    return await response.json();
}
// Load and display text files
async function loadTextFiles() {
    // Best solution
    const bestSolution = await fetchJSON("/final-results");
    document.querySelector("#best-solution pre").textContent = JSON.stringify(bestSolution, null, 2);

    // Profiler summary
    const profilerSummaryData = await fetchJSON("/call-counts");
    document.querySelector("#profiler-summary pre").textContent = JSON.stringify(profilerSummaryData, null, 2);

}

function setupCharts() {
    d3.selectAll("svg")
        .attr("width", "100%")
        .attr("height", 400);
}

function drawBarChart(svg, data, xKey, yKey) {
    svg.selectAll("*").remove();

    // Scale avg_time by 100000 for visibility
    const scaledData = data.map(d => ({
        ...d,
        scaled_time: +d[yKey] * 100000  // ensure numeric
    }));

    const width = 800;
    const height = 400;
    const margin = { top: 30, right: 20, bottom: 120, left: 80 };

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // X scale
    const x = d3.scaleBand()
        .domain(scaledData.map(d => d[xKey]))
        .range([0, innerWidth])
        .padding(0.1);

    // Y scale
    const y = d3.scaleLinear()
        .domain([0, d3.max(scaledData, d => d.scaled_time)])
        .range([innerHeight, 0])
        .nice();

    // X axis
    g.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end")
        .style("font-size", "10px");

    // Y axis
    g.append("g")
        .call(d3.axisLeft(y));

    // Bars
    g.selectAll("rect")
        .data(scaledData)
        .join("rect")
        .attr("x", d => x(d[xKey]))
        .attr("y", d => y(d.scaled_time))
        .attr("width", x.bandwidth())
        .attr("height", d => innerHeight - y(d.scaled_time))
        .attr("fill", "steelblue");

    // Y label
    g.append("text")
        .attr("x", -innerHeight / 2)
        .attr("y", -margin.left + 20)
        .attr("transform", "rotate(-90)")
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .attr("fill", "white")
        .text("Average Time (ms)");

    // Title
    g.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", -10)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .attr("fill", "white")
        .text("Average Time per Function");
}

async function loadD3Visualizations() {
    // Fetch the profiler data
    const profilerData = await fetchJSON("/call-counts");

    // Draw the bar chart with function vs avg_time
    const svg1 = d3.select("#time-profile-chart svg");
    drawBarChart(svg1, profilerData, "function", "avg_time");
}


// Initialize everything
async function init() {
    await loadTextFiles();
    setupCharts();
    await loadD3Visualizations();
}

// Start
init();
// Helper functions
async function fetchText(url) {
    const response = await fetch(url);
    return await response.text();
}

async function fetchJSON(url) {
    const response = await fetch(url);
    return await response.json();
}

// Parse profiler text into structured data
async function parseProfilerText(url) {
    const text = await fetchText(url);
    const lines = text.split("\n").slice(2); // skip header
    const data = lines.map(line => {
        const parts = line.trim().split(/\s+/);
        return {
            function: parts[0],
            calls: +parts[1],
            total_time: +parts[2],
            avg_time: +parts[3]
        };
    });
    return data;
}

// Load and display text files
async function loadTextFiles() {
    // Best solution
    const bestSolution = await fetchJSON("http://ta-backend:5001/final-results");
    document.querySelector("#best-solution pre").textContent = bestSolution;

    // Profiler summary
    const profilerSummaryData = await fetchJSON("http://ta-backend:5001/time-profile");
    document.querySelector("#profiler-summary pre").textContent = JSON.stringify(profilerSummaryData, null, 2);

    // Summary CSV head
    const summaryCSV = await fetchJSON("http://ta-backend:5001/summary-csv");
    document.querySelector("#summary-csv pre").textContent = summaryCSV.split("\n").slice(0, 6).join("\n");
}

// Setup SVGs
function setupCharts() {
    d3.selectAll("svg")
        .attr("width", "100%")
        .attr("height", 400);
}

// Generic bar chart function
function drawBarChart(svg, data, xKey, yKey) {
    const width = parseInt(svg.style("width"));
    const height = parseInt(svg.style("height"));

    const x = d3.scaleBand()
        .domain(data.map(d => d[xKey]))
        .range([0, width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d[yKey])])
        .range([height, 0]);

    svg.selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", d => x(d[xKey]))
        .attr("y", d => y(d[yKey]))
        .attr("width", x.bandwidth())
        .attr("height", d => height - y(d[yKey]))
        .attr("fill", "white");
}

// Load and render D3 charts
async function loadD3Visualizations() {
    // Time profile chart
    const timeProfileData = await fetchJSON("http://ta-backend:5001/time-profile");
    const svg1 = d3.select("#time-profile-chart svg");
    drawBarChart(svg1, timeProfileData, "function", "time");
    
    // Final results chart
    const finalResultsData = await fetchJSON("http://ta-backend:5001/final-results");
    const svg2 = d3.select("#final-results-chart svg");
    drawBarChart(svg2, finalResultsData, "metric", "value");

    // Call counts chart
    const callCountsData = await fetchJSON("http://ta-backend:5001/call-counts");
    const svg3 = d3.select("#call-counts-chart svg");
    drawBarChart(svg3, callCountsData, "function", "calls");
}

// Initialize everything
async function init() {
    await loadTextFiles();
    setupCharts();
    await loadD3Visualizations();
}

// Start
init();

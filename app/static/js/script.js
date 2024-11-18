// app/static/js/script.js

document
  .getElementById("optimization-form")
  .addEventListener("submit", function (e) {
    e.preventDefault();

    // Hide previous results
    document.getElementById("results").style.display = "none";

    // Show loading spinner
    document.getElementById("loading").style.display = "block";

    // Gather form data
    const num_blocks = document.getElementById("num_blocks").value;
    const layers = document.getElementById("layers").value;
    const connections_per_block = document.getElementById(
      "connections_per_block"
    ).value;
    const floorplan_size = document.getElementById("floorplan_size").value;

    // Prepare payload
    const payload = {
      num_blocks: parseInt(num_blocks),
      layers: parseInt(layers),
      connections_per_block: parseInt(connections_per_block),
      floorplan_size: parseInt(floorplan_size),
    };

    // Send POST request to backend
    fetch("/optimize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        // Hide loading spinner
        document.getElementById("loading").style.display = "none";

        if (data.status === "success") {
          // Populate results
          document.getElementById("initial_energy").innerText =
            data.initial_energy;
          document.getElementById("optimized_energy").innerText =
            data.optimized_energy;
          document.getElementById("area_reduction").innerText =
            data.area_reduction;
          document.getElementById("interconnect_reduction").innerText =
            data.interconnect_reduction;
          document.getElementById("power_reduction").innerText =
            data.power_reduction;
          document.getElementById("initial_temp").innerText = data.initial_temp;
          document.getElementById("optimized_temp").innerText =
            data.optimized_temp;
          document.getElementById("execution_time").innerText =
            data.execution_time;

          // Set download link
          document.getElementById("download_csv").href = data.download_csv;

          // Display initial images
          const initialImagesDiv = document.getElementById("initial_images");
          initialImagesDiv.innerHTML = "";
          data.initial_images.forEach((path) => {
            const col = document.createElement("div");
            col.className = "col-md-4";
            const img = document.createElement("img");
            img.src = "/" + path;
            img.alt = "Initial Floorplan Layer";
            img.className = "img-fluid mb-3";
            col.appendChild(img);
            initialImagesDiv.appendChild(col);
          });

          // Display optimized images
          const optimizedImagesDiv =
            document.getElementById("optimized_images");
          optimizedImagesDiv.innerHTML = "";
          data.optimized_images.forEach((path) => {
            const col = document.createElement("div");
            col.className = "col-md-4";
            const img = document.createElement("img");
            img.src = "/" + path;
            img.alt = "Optimized Floorplan Layer";
            img.className = "img-fluid mb-3";
            col.appendChild(img);
            optimizedImagesDiv.appendChild(col);
          });

          // Populate CSV table
          const csvTableHead = document.getElementById("csv_table_head");
          const csvTableBody = document.getElementById("csv_table_body");
          csvTableHead.innerHTML = "";
          csvTableBody.innerHTML = "";

          if (data.csv_data.length > 0) {
            // Create table headers
            const headers = Object.keys(data.csv_data[0]);
            const headerRow = document.createElement("tr");
            headers.forEach((header) => {
              const th = document.createElement("th");
              th.innerText = header;
              headerRow.appendChild(th);
            });
            csvTableHead.appendChild(headerRow);

            // Create table rows
            data.csv_data.forEach((row) => {
              const tr = document.createElement("tr");
              headers.forEach((header) => {
                const td = document.createElement("td");
                td.innerText = row[header];
                tr.appendChild(td);
              });
              csvTableBody.appendChild(tr);
            });
          } else {
            csvTableHead.innerHTML = "<tr><th>No data available</th></tr>";
            csvTableBody.innerHTML = "<tr><td>No data available</td></tr>";
          }

          // Populate Initial Block Placements
          const initialBlockPlacements =
            data.csv_data.length > 0
              ? data.csv_data[data.csv_data.length - 1][
                  "Initial Block Placements"
                ].split("; ")
              : [];
          const placementsList = document.getElementById(
            "initial_block_placements"
          );
          placementsList.innerHTML = "";
          initialBlockPlacements.forEach((placement) => {
            const li = document.createElement("li");
            li.className = "list-group-item";
            li.innerText = placement;
            placementsList.appendChild(li);
          });

          // Show results
          document.getElementById("results").style.display = "block";
        } else {
          alert("Error: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        document.getElementById("loading").style.display = "none";
        alert("An error occurred while processing your request.");
      });
  });

"use client";

import React, { useState, useEffect } from "react";
import {
  Button,
  Box,
  Typography,
  TextField,
  IconButton,
  Card,
  CardContent,
  CardActions,
  Grid,
  Tooltip,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete"; // Ensure this is imported
import MenuBar from "../components/MenuBar";
import CommentButton from "../components/comment";
import { useRouter } from "next/navigation";

export default function LuPage() {
  const router = useRouter();
  const ROWS = 8;
  const COLS = 12;

  // Initialize grid state
  const [grid, setGrid] = useState(() =>
    Array.from({ length: ROWS }, (_, rowIndex) =>
      Array.from({ length: COLS }, (_, colIndex) => ({
        position: `${8 - rowIndex < 10 ? "0" : ""}${8 - rowIndex},${
          colIndex + 1 < 10 ? "0" : ""
        }${colIndex + 1}`,
        weight: "00000",
        status: "UNUSED",
      }))
    )
  );

  // BUFFER to hold containers temporarily
  const [buffer, setBuffer] = useState([]);

  // State for response data
  const [responseData, setResponseData] = useState(null);

  // Visualization states
  const [currentMoveIndex, setCurrentMoveIndex] = useState(0);
  const [currentMoveMessage, setCurrentMoveMessage] = useState("");

  // Loading and error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeStamp, setTimeStamp] = useState("");

  // Mode states
  const [mode, setMode] = useState(null); // 'loading', 'unloading', or null
  const [highlightedCells, setHighlightedCells] = useState([]);
  const [selectedUnloadCells, setSelectedUnloadCells] = useState([]);

  // Container weight mapping
  const [containerWeights, setContainerWeights] = useState({});

  // Load Queue
  const [loadQueue, setLoadQueue] = useState([]);

  // Inputs for adding containers to the load queue
  const [newContainer, setNewContainer] = useState({
    name: "",
    weight: "",
  });

  // State to track if all moves have been processed
  const [allMovesProcessed, setAllMovesProcessed] = useState(false);

  // Reset selections after operations
  const resetSelections = () => {
    setSelectedUnloadCells([]);
    setMode(null);
    setCurrentMoveIndex(0);
    setCurrentMoveMessage("");
  };

  // Log changes to responseData for debugging
  useEffect(() => {
    console.log("responseData Updated:", responseData);
  }, [responseData]);

  // Fetch initial grid data on component mount
  useEffect(() => {
    async function fetchInitialData() {
      try {
        const response = await fetch("http://127.0.0.1:5000/api/get_grid_data");
        if (!response.ok) {
          throw new Error("Failed to fetch initial grid data.");
        }
        const result = await response.json();
        const fetchedData = result.data;

        const updatedGrid = grid.map((row) => [...row]);
        const weightsMapping = {};

        fetchedData.forEach((cell) => {
          const [r, c] = cell.position.split(",").map(Number);
          updatedGrid[8 - r][c - 1] = cell;

          // Build containerWeights mapping
          if (cell.status !== "UNUSED" && cell.status !== "NAN") {
            if (!weightsMapping[cell.status]) {
              weightsMapping[cell.status] = cell.weight;
            }
          }
        });

        setGrid(updatedGrid);
        setContainerWeights(weightsMapping);
        console.log("Initial grid data fetched and set.");
      } catch (err) {
        setError(err.message);
        console.error("Error fetching initial grid data:", err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchInitialData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Helper function to check valid positions
  const isValidPosition = (row, col) => {
    return row >= 1 && row <= ROWS && col >= 1 && col <= COLS;
  };

  // Update highlighted cells based on mode and selections
  const updateHighlightedCells = () => {
    const highlighted = [];
    for (let row = 0; row < ROWS; row++) {
      for (let col = 0; col < COLS; col++) {
        const cell = grid[row]?.[col]; // Safely access the cell
        if (!cell) continue; // Skip if the cell is undefined

        if (
          mode === "unloading" ||
          selectedUnloadCells.includes(cell.position)
        ) {
          // Highlight cells that are FILLED for unloading
          if (cell.status !== "NAN" && cell.status !== "UNUSED") {
            highlighted.push(cell.position);
          }
        }
      }
    }
    setHighlightedCells(highlighted);
    console.log("Highlighted Cells Updated:", highlighted);
  };

  useEffect(() => {
    updateHighlightedCells();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, grid, selectedUnloadCells]);

  // Handle mode switching between 'loading' and 'unloading'
  const handleModeSwitch = (newMode) => {
    setMode(newMode);
    // Clear selections when switching modes
    setSelectedUnloadCells([]);
    setCurrentMoveMessage("");
    setAllMovesProcessed(false); // Reset the flag
    console.log(`Mode switched to: ${newMode}`);
  };

  // Handle grid cell clicks based on current mode
  const handleGridClick = (position) => {
    if (!highlightedCells.includes(position)) {
      // Clicked cell is not highlighted; no action
      return;
    }

    if (mode === "unloading") {
      // Toggle selection for unloading
      setSelectedUnloadCells((prev) =>
        prev.includes(position)
          ? prev.filter((cell) => cell !== position)
          : [...prev, position]
      );
      console.log(
        `Toggle selection for unloading. Selected Cells: ${[
          ...selectedUnloadCells,
          position,
        ]}`
      );
    }
  };

  // **New Function:** Add container to load queue
  const handleAddToLoadQueue = () => {
    const { name, weight } = newContainer;
    if (name.trim() === "" || weight.trim() === "") {
      alert("Please enter both container name and weight.");
      return;
    }

    // Validate weight is a positive number
    const weightNum = parseInt(weight, 10);
    if (isNaN(weightNum) || weightNum <= 0) {
      alert("Please enter a valid positive number for weight.");
      return;
    }

    // Optional: Check for duplicate container names
    if (loadQueue.some((container) => container.name === name.trim())) {
      alert("Container name must be unique.");
      return;
    }

    setLoadQueue((prevQueue) => [
      ...prevQueue,
      { name: name.trim(), weight: weightNum.toString().padStart(5, "0") },
    ]);

    // Reset input fields
    setNewContainer({ name: "", weight: "" });
    console.log(`Added container to load queue: ${name.trim()}`);
  };

  // **New Function:** Remove container from load queue
  const handleRemoveFromLoadQueue = (index) => {
    const removed = loadQueue[index];
    setLoadQueue((prevQueue) => prevQueue.filter((_, i) => i !== index));
    console.log(`Removed container from load queue: ${removed.name}`);
  };

  // Handle final confirmation of load/unload actions
  const handleFinalConfirm = () => {
    if (loadQueue.length > 0 || selectedUnloadCells.length > 0) {
      sendDataToAPI();
    } else {
      alert("Please add containers to load or select containers to unload.");
    }
  };

  // Send load/unload data to the API
  const sendDataToAPI = async () => {
    const clickTime = new Date();
    const loadContainers = loadQueue.map((container) => ({
      containerName: container.name,
      weight: container.weight,
      location: "External", // Assuming loading from an external location
    }));
    const unloadContainers = selectedUnloadCells.map((pos) => {
      const [r, c] = pos.split(",").map(Number);
      return grid[8 - r][c - 1];
    });

    const payload = { load: loadContainers, unload: unloadContainers };

    try {
      const response = await fetch("http://127.0.0.1:5000/api/load_unload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to post data to /api/load_unload");
      }

      const result = await response.json();
      const totalTime = result.total_time;
      const endTimeDate = new Date(clickTime.getTime() + totalTime * 60000); // Add minutes

      // Helper function to format time in military format
      const formatTimeMilitary = (date) => {
        const hours = date.getHours().toString().padStart(2, "0");
        const minutes = date.getMinutes().toString().padStart(2, "0");
        return `${hours}:${minutes}`;
      };

      const formattedEndTime = formatTimeMilitary(endTimeDate);
      setTimeStamp(formattedEndTime);
      setResponseData(result); // Save the response directly for processing
      setCurrentMoveIndex(0); // Reset move index
      console.log("Server Response:", result);
    } catch (error) {
      setError(error.message);
      console.error("Error posting data:", error.message);
      alert(`Error: ${error.message}`);
    }

    resetSelections();
  };

  // Handle execution of the next move in the responseData
  const handleNextMove = () => {
    if (!responseData) {
      setCurrentMoveMessage("No moves to process.");
      return;
    }

    const totalUnloadMoves = responseData.unloadMoves.length;
    const totalLoadMoves = responseData.loadMoves.length;
    const totalMoves = totalUnloadMoves + totalLoadMoves;

    if (currentMoveIndex >= totalMoves) {
      setCurrentMoveMessage("All moves have been processed.");
      return;
    }

    let move;
    if (currentMoveIndex < totalUnloadMoves) {
      move = responseData.unloadMoves[currentMoveIndex];
      executeMove(move, "unload");
    } else {
      const loadMoveIndex = currentMoveIndex - totalUnloadMoves;
      move = responseData.loadMoves[loadMoveIndex];
      executeMove(move, "load");
    }

    setCurrentMoveIndex((prev) => prev + 1);
    console.log(`Processed move ${currentMoveIndex + 1}:`, move);
  };

  // Execute a single move based on its type
  const executeMove = async (move, moveCategory) => {
    // Generate a descriptive message for the move
    let message = "";
    console.log("Executing move:", move);

    switch (moveCategory) {
      case "unload":
        if (
          move.to !== "UNLOAD" &&
          move.to !== "BUFFER" &&
          move.from !== "BUFFER"
        ) {
          // Move from grid cell to another grid cell
          const [fromRow, fromCol] = move.from;
          const [toRow, toCol] = move.to;
          setGrid((prevGrid) => {
            const updatedGrid = prevGrid.map((rowArr) => [...rowArr]);
            const fromGridRow = 8 - fromRow;
            const fromGridCol = fromCol - 1;
            const toGridRow = 8 - toRow;
            const toGridCol = toCol - 1;
            const container = updatedGrid[fromGridRow][fromGridCol];
            if (
              container.status !== "UNUSED" &&
              container.status !== "NAN" &&
              isValidPosition(toRow, toCol)
            ) {
              // Move container to new position
              updatedGrid[toGridRow][toGridCol] = {
                status: container.status,
                weight: container.weight,
              };
              // Clear the original position
              updatedGrid[fromGridRow][fromGridCol] = {
                status: "UNUSED",
                weight: "00000",
              };
              message = `Moved ${move.container} from [${fromRow},${fromCol}] to [${toRow},${toCol}].`;
            } else {
              console.warn(
                `Cannot move container ${container.status} from [${fromRow}, ${fromCol}] to [${toRow}, ${toCol}].`
              );
              message = `Cannot move container from [${fromRow},${fromCol}] to [${toRow},${toCol}].`;
            }
            return updatedGrid;
          });
        } else if (move.to === "BUFFER") {
          // Move from grid cell to BUFFER
          const [row, col] = move.from;
          setGrid((prevGrid) => {
            const updatedGrid = prevGrid.map((rowArr) => [...rowArr]);
            const gridRow = 8 - row;
            const gridCol = col - 1;
            const container = updatedGrid[gridRow][gridCol];
            if (container.status !== "UNUSED" && container.status !== "NAN") {
              // Add to buffer
              setBuffer((prevBuffer) => [
                ...prevBuffer,
                { ...container, original_position: [row, col] },
              ]);
              // Remove from grid
              updatedGrid[gridRow][gridCol] = {
                status: "UNUSED",
                weight: "00000",
              };
              message = `Moved ${move.container} from [${row},${col}] to BUFFER.`;
              console.log(buffer);
            } else {
              console.warn(
                `Cannot move container ${container.status} from [${row}, ${col}] to BUFFER.`
              );
              message = `Cannot move container from [${row},${col}] to BUFFER.`;
            }
            return updatedGrid;
          });
        } else if (move.to === "UNLOAD") {
          // Unload completely from grid
          const [row, col] = move.from;
          setGrid((prevGrid) => {
            const updatedGrid = prevGrid.map((rowArr) => [...rowArr]);
            const gridRow = 8 - row;
            const gridCol = col - 1;
            const container = updatedGrid[gridRow][gridCol];
            if (container.status !== "UNUSED" && container.status !== "NAN") {
              // Remove from grid
              updatedGrid[gridRow][gridCol] = {
                status: "UNUSED",
                weight: "00000",
              };
              message = `Unloaded ${move.container} from [${row},${col}].`;
            } else {
              console.warn(
                `Cannot unload container at [${row}, ${col}] as it is already UNUSED or NAN.`
              );
              message = `Cannot unload container at [${row},${col}] as it is already UNUSED or NAN.`;
            }
            return updatedGrid;
          });
        } else if (move.from === "BUFFER") {
          // Move from BUFFER to grid cell
          const [row, col] = move.to;
          const name = move.container;
          setGrid((prevGrid) => {
            const updatedGrid = prevGrid.map((rowArr) => [...rowArr]);
            const gridRow = 8 - row;
            const gridCol = col - 1;
            const bufferIndex = buffer.findIndex(
              (container) => container.status === name
            );
            if (bufferIndex !== -1) {
              const container = buffer[bufferIndex];
              // Add to grid
              updatedGrid[gridRow][gridCol] = {
                status: container.status,
                weight: container.weight,
              };
              // Remove from buffer
              setBuffer((prevBuffer) =>
                prevBuffer.filter((_, index) => index !== bufferIndex)
              );
              message = `Moved ${container.status} from BUFFER to [${row},${col}].`;
            } else {
              console.warn(
                `Cannot move container from BUFFER to [${row},${col}] as it is not found in the buffer.`
              );
              message = `Cannot move container from BUFFER to [${row},${col}] as it is not found in the buffer.`;
            }
            return updatedGrid;
          });
        } else {
          console.warn(`Unknown unload move destination: ${move.to}`);
          message = `Unknown unload move destination: ${move.to}`;
        }
        break;

      case "load":
        const [row, col] = move.position;
        setGrid((prevGrid) => {
          const updatedGrid = prevGrid.map((rowArr) => [...rowArr]);
          const gridRow = 8 - row;
          const gridCol = col - 1;
          if (updatedGrid[gridRow][gridCol].status === "UNUSED") {
            updatedGrid[gridRow][gridCol] = {
              status: move.container,
              weight: containerWeights[move.weight] || "00000",
              position: row,
              col,
            };
            message = `Loaded ${move.container} to [${row},${col}].`;
          } else {
            console.warn(
              `Cannot load container ${move.container} to [${row},${col}] as the cell is already occupied.`
            );
            message = `Failed to load ${move.container} to [${row},${col}]. Cell is occupied.`;
          }
          return updatedGrid;
        });
        break;

      default:
        message = `Unhandled move category: ${moveCategory}`;
        console.warn(`Unhandled move category: ${moveCategory}`);
        break;
    }

    setCurrentMoveMessage(message);
    try {
      const logMessage = message;
      const logResponse = await fetch("http://127.0.0.1:5000/api/log_action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: logMessage }),
      });

      if (!logResponse.ok) {
        console.error("Failed to log ship movement");
      }
    } catch (err) {
      console.error("Error logging movement:", err);
    }
    console.log("Move executed:", message);
  };

  // **New useEffect:** Monitor when all moves have been processed
  useEffect(() => {
    if (currentMoveMessage === "All moves have been processed.") {
      // Empty the load queue
      setLoadQueue([]);
      // Hide the "Next Move" button by clearing responseData
      setResponseData(null);
      // Set the flag to render the "Confirm" button
      setAllMovesProcessed(true);
      console.log(
        "All moves processed. Load queue emptied and 'Next Move' button hidden."
      );
    }
  }, [currentMoveMessage]);

  // **New Function:** Handle Confirm Button Click
  const handleConfirm = async () => {
    // Prepare the data to send (only grid, as backend handles filename)
    const payload = grid;

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/finalize_load_unload",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to finalize Load/Unload manifest.");
      }

      const result = await response.json();
      console.log("Finalize Response:", result);
      alert(
        "Successfully saved outbound manifest. Please email the manifest to the customer."
      );

      // Navigate back to the main page
      router.push("/main");
    } catch (error) {
      console.error("Error finalizing Load/Unload manifest:", error);
      alert(`Error: ${error.message}`);
    }
  };

  // Render loading state
  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <p>Loading...</p>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <p style={{ color: "red" }}>Error: {error}</p>
      </div>
    );
  }

  return (
    <div>
      <MenuBar />
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          gap: 2,
          mt: 2,
        }}
      >
        <Button
          variant="contained"
          color="success"
          onClick={() => handleModeSwitch("loading")}
          sx={{ fontWeight: "bold" }}
          disabled={responseData !== null} // Disable if moves are being processed
        >
          Loading
        </Button>
        <Button
          variant="contained"
          color="error"
          onClick={() => handleModeSwitch("unloading")}
          sx={{ fontWeight: "bold" }}
          disabled={responseData !== null} // Disable if moves are being processed
        >
          Unloading
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleFinalConfirm}
          sx={{ fontWeight: "bold" }}
          disabled={loadQueue.length === 0 && selectedUnloadCells.length === 0}
        >
          Confirm
        </Button>
      </Box>
      <Typography variant="h6" sx={{ textAlign: "center", mt: 2 }}>
        Current Mode:{" "}
        {mode === "loading"
          ? "Loading Containers"
          : mode === "unloading"
          ? "Unloading Containers"
          : "None"}
      </Typography>

      {/* **Load Containers Form**: Visible only in "loading" mode */}
      {mode === "loading" && (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            mt: 4,
          }}
        >
          <Typography variant="h6">Add Containers to Load Queue</Typography>
          <Box
            sx={{
              display: "flex",
              gap: 2,
              mt: 2,
              flexWrap: "wrap",
              justifyContent: "center",
            }}
          >
            <TextField
              label="Container Name"
              value={newContainer.name}
              onChange={(e) =>
                setNewContainer((prev) => ({
                  ...prev,
                  name: e.target.value,
                }))
              }
              variant="outlined"
              size="small" // Smaller input fields
            />
            <TextField
              label="Weight"
              type="number"
              value={newContainer.weight}
              onChange={(e) =>
                setNewContainer((prev) => ({
                  ...prev,
                  weight: e.target.value,
                }))
              }
              variant="outlined"
              size="small" // Smaller input fields
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleAddToLoadQueue}
              sx={{ height: "40px" }} // Reduced height
            >
              Add
            </Button>
          </Box>
        </Box>
      )}

      {/* **Load Queue Display**: Always visible if loadQueue has items */}
      {loadQueue.length > 0 && (
        <Box sx={{ width: "80%", mt: 4, marginX: "auto" }}>
          <Typography variant="h6" gutterBottom>
            Load Queue
          </Typography>
          <Grid container spacing={1}>
            {" "}
            {/* Reduced spacing */}
            {loadQueue.map((container, index) => (
              <Grid
                item
                xs={12}
                sm={6}
                md={4}
                lg={3}
                key={`${container.name}-${index}`}
              >
                <Card
                  variant="outlined"
                  sx={{
                    minWidth: 150, // Set a minimum width
                    maxWidth: 200, // Set a maximum width
                    padding: 0.5, // Reduce padding
                    height: "120px", // Consistent height
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                  }}
                >
                  <CardContent sx={{ padding: "8px" }}>
                    {" "}
                    {/* Reduced padding */}
                    <Typography
                      variant="subtitle1" // Smaller font size
                      component="div"
                      sx={{
                        fontWeight: "bold",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {container.name}
                    </Typography>
                    <Typography
                      variant="body2" // Smaller font size
                      color="text.secondary"
                      sx={{
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      Weight: {container.weight}
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ padding: "4px" }}>
                    {" "}
                    {/* Reduced padding */}
                    <IconButton
                      aria-label="delete"
                      size="small" // Smaller icon button
                      onClick={() => handleRemoveFromLoadQueue(index)}
                    >
                      <DeleteIcon fontSize="small" /> {/* Smaller icon */}
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Visualization Controls */}
      {responseData && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 2,
            mt: 2,
          }}
        >
          <Button
            variant="contained"
            color="secondary"
            onClick={handleNextMove}
            sx={{ fontWeight: "bold" }}
          >
            Next Move
          </Button>
          <Typography variant="subtitle1">{currentMoveMessage}</Typography>
        </Box>
      )}

      {/* **Confirm Button**: Rendered after all moves are processed */}
      {allMovesProcessed && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            mt: 2,
          }}
        >
          <Button
            variant="contained"
            color="success"
            onClick={handleConfirm}
            sx={{ fontWeight: "bold" }}
          >
            Confirm
          </Button>
        </Box>
      )}

      {/* Visualization Grid and BUFFER */}
      <Box
        sx={{
          marginTop: 4,
          display: "flex",
          justifyContent: "center",
          gap: 4,
          flexWrap: "wrap",
        }}
      >
        {/* **New Addition: Operation Timestamp Card** */}
        {timeStamp && (
          <Card
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              border: "1px solid #ddd",
              padding: 2,
              borderRadius: 2,
              height: "fit-content",
              minWidth: 200,
              maxWidth: 250,
              boxShadow: 3,
              backgroundColor: "#f5f5f5",
            }}
          >
            <CardContent>
              <Typography variant="h6" component="div">
                Operation Complete At: {timeStamp}
              </Typography>
              
            </CardContent>
          </Card>
        )}

        {/* Main Grid */}
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(12, 60px)",
            gridTemplateRows: "repeat(8, 60px)",
            gap: 1,
            justifyContent: "center",
          }}
        >
          {grid.flat().map((cell) => (
            <div
              key={cell.position}
              style={{
                width: 60,
                height: 60,
                backgroundColor: selectedUnloadCells.includes(cell.position)
                  ? "lightcoral"
                  : cell.status === "NAN"
                  ? "#555"
                  : cell.status === "UNUSED"
                  ? "#ccc"
                  : "green",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border: highlightedCells.includes(cell.position)
                  ? "2px dashed"
                  : "1px solid #ddd",
                cursor: highlightedCells.includes(cell.position)
                  ? "pointer"
                  : "default",
                color:
                  cell.status === "UNUSED" || cell.status === "NAN"
                    ? "black"
                    : "white",
                fontWeight:
                  cell.status === "UNUSED" || cell.status === "NAN"
                    ? "normal"
                    : "bold",
              }}
              onClick={() => handleGridClick(cell.position)}
            >
              {cell.status !== "NAN" && cell.status !== "UNUSED" && cell.status}
            </div>
          ))}
        </Box>

        {/* BUFFER Display */}
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            border: "1px solid #ddd",
            padding: 2,
            borderRadius: 2,
            height: "fit-content",
          }}
        >
          <Typography variant="h6">BUFFER</Typography>
          {buffer.length === 0 ? (
            <Typography>No containers in BUFFER</Typography>
          ) : (
            buffer.map((container, index) => (
              <Box
                key={`${container.name}-${container.original_position}-${index}`} // Unique key
                sx={{
                  width: 80,
                  height: 60,
                  backgroundColor: "yellow",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  marginTop: 1,
                  border: "1px solid #999",
                  overflow: "hidden",
                  // Removed textOverflow and whiteSpace from Box as Typography handles it
                  fontSize: "0.8rem",
                }}
              >
                <Tooltip title={container.status} arrow>
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: "bold",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      width: "100%", // Ensure the Typography takes full width of the Box
                      textAlign: "center", // Center the text horizontally
                    }}
                  >
                    {container.status}
                  </Typography>
                </Tooltip>
              </Box>
            ))
          )}
        </Box>
      </Box>

      {/* Move Description */}
      {currentMoveMessage && (
        <Typography variant="subtitle1" sx={{ textAlign: "center", mt: 2 }}>
          {currentMoveMessage}
        </Typography>
      )}

      <CommentButton />
    </div>
  );
}

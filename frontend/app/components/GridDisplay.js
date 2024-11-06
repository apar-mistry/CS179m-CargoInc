"use client";
import React, { useEffect, useState } from "react";
import { Container, Typography, Box, Paper } from "@mui/material";
import axios from "axios";

const GridDisplay = () => {
  // Initialize an 8x12 grid with bottom row as row 1
  const [gridData, setGridData] = useState(
    Array.from({ length: 8 }, (_, rowIndex) =>
      Array.from({ length: 12 }, (_, colIndex) => ({
        position: `${8 - rowIndex < 10 ? '0' : ''}${8 - rowIndex},${colIndex + 1 < 10 ? '0' : ''}${colIndex + 1}`,
        weight: "00000",
        status: "NAN", // Default to "NAN" to indicate an empty cell
      }))
    )
  );

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch data from backend
        const response = await axios.get("http://127.0.0.1:5000/api/get_grid_data");
        const fetchedData = response.data.data;

        // Clone the existing grid to update it based on fetched data
        const updatedGrid = [...gridData];
        
        // Populate the grid using position data from the backend
        fetchedData.forEach((cell) => {
          const [row, col] = cell.position.split(",").map(Number);
          updatedGrid[8 - row][col - 1] = cell; // Update specific cell based on adjusted position
        });
        
        setGridData(updatedGrid);
      } catch (error) {
        console.error("Error fetching grid data:", error);
      }
    };

    fetchData();
  }, []);

  const renderGridCell = (cell) => {
    const isDarkGray = cell.status === "NAN";
    const isLightGray = cell.status === "UNUSED";
    
    return (
      <Paper
        key={cell.position}
        sx={{
          width: 60,
          height: 60,
          backgroundColor: isDarkGray ? "#555" : isLightGray ? "#ccc" : "#f0f0f0", // Dark gray for "NAN", light gray for "UNUSED"
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          border: "1px solid #ddd",
        }}
      >
        {!isDarkGray && !isLightGray && (
          <>
            <Typography variant="body2">{`${cell.status}`}</Typography>
          </>
        )}
      </Paper>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ marginTop: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>
        Ship Grid Display
      </Typography>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(12, 60px)", // 12 columns with fixed cell width
          gridTemplateRows: "repeat(8, 60px)",     // 8 rows with fixed cell height
          gap: 1,
          justifyContent: "center",
        }}
      >
        {gridData.flat().map((cell) => renderGridCell(cell))}
      </Box>
    </Container>
  );
};

export default GridDisplay;
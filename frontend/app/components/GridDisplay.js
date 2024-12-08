"use client";

import React from "react";
import { Container, Typography, Box, Paper } from "@mui/material";

export default function GridDisplay({ grid, highlightCoord, destinationCoord }) {
  const isHighlightCell = (cell) => {
    if (!highlightCoord) return false;
    const [row, col] = cell.position.split(",").map(Number);
    return highlightCoord.row === row && highlightCoord.col === col;
  };

  const isDestinationCell = (cell) => {
    if (!destinationCoord) return false;
    const [row, col] = cell.position.split(",").map(Number);
    return destinationCoord.row === row && destinationCoord.col === col;
  };

  const renderGridCell = (cell) => {
    const isDarkGray = cell.status === "NAN";
    const isLightGray = cell.status === "UNUSED";

    let borderStyle = "1px solid #ddd";
    if (isHighlightCell(cell)) {
      borderStyle = "2px solid yellow";
    } else if (isDestinationCell(cell)) {
      borderStyle = "2px solid green";
    }

    return (
      <Paper
        key={cell.position}
        sx={{
          width: 60,
          height: 60,
          backgroundColor: isDarkGray ? "#555" : isLightGray ? "#ccc" : "#f0f0f0",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          border: borderStyle,
        }}
      >
        {!isDarkGray && !isLightGray && (
          <Typography variant="body2">{cell.status}</Typography>
        )}
      </Paper>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ marginTop: 4 }}>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(12, 60px)",
          gridTemplateRows: "repeat(8, 60px)",
          gap: 1,
          justifyContent: "center",
        }}
      >
        {grid.flat().map((cell) => renderGridCell(cell))}
      </Box>
    </Container>
  );
}
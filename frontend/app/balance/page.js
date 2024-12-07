"use client";

import { useState, useEffect } from "react";
import { CircularProgress, Box, Typography, Button, Alert, Card, CardContent, Dialog, DialogActions, DialogTitle } from "@mui/material";
import MenuBar from "../components/MenuBar";
import GridDisplay from "../components/GridDisplay";
import CommentButton from "../components/comment";
import { useRouter } from 'next/navigation'; 

export default function BalancePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [moves, setMoves] = useState([]);
  // currentMoveIndex tracks which move we are on
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);
  const [cost, setCost] = useState(0);
  const [time, setTime] = useState(null);

  const ROWS = 8;
  const COLS = 12;

  const [grid, setGrid] = useState(() =>
    Array.from({ length: ROWS }, (_, rowIndex) =>
      Array.from({ length: COLS }, (_, colIndex) => ({
        position: `${8 - rowIndex < 10 ? "0" : ""}${8 - rowIndex},${colIndex + 1 < 10 ? "0" : ""}${colIndex + 1}`,
        weight: "00000",
        status: "NAN"
      }))
    )
  );

  const [highlightCoord, setHighlightCoord] = useState(null);
  const [destinationCoord, setDestinationCoord] = useState(null);

  const [openDialog, setOpenDialog] = useState(false);

  // showHighlightOnly will be toggled after the first highlight
  // Initially, when the user clicks "Begin Balance" (the first "Next"), we want to highlight only.
  const [showHighlightOnly, setShowHighlightOnly] = useState(true);

  useEffect(() => {
    async function fetchInitialData() {
      try {
        const now = new Date();
        const gridResponse = await fetch("http://127.0.0.1:5000/api/get_grid_data");
        if (!gridResponse.ok) {
          throw new Error("Failed to fetch initial grid data.");
        }
        const gridResult = await gridResponse.json();
        const fetchedData = gridResult.data;

        const updatedGrid = grid.map((row) => [...row]);
        fetchedData.forEach((cell) => {
          const [r, c] = cell.position.split(",").map(Number);
          updatedGrid[8 - r][c - 1] = cell;
        });
        setGrid(updatedGrid);

        const movesResponse = await fetch("http://127.0.0.1:5000/api/balance");
        if (!movesResponse.ok) {
          throw new Error("Failed to fetch balance data.");
        }
        const movesResult = await movesResponse.json();
        setMoves(movesResult.Data || []);
        setCost(movesResult.Cost || 0);

        const costInMinutes = movesResult.Cost || 0;
        const endTime = new Date(now.getTime() + costInMinutes * 60000);
        const endTimeStr = endTime.toTimeString().slice(0, 5);
        setTime(endTimeStr);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchInitialData();
  }, []);

  const handleNext = async () => {
    if (moves.length === 0) return;
  
    const nextMoveIndex = showHighlightOnly ? currentMoveIndex + 1 : currentMoveIndex;
    if (nextMoveIndex < moves.length) {
      const [initialRow, initialCol, newRow, newCol] = moves[nextMoveIndex];
      const updatedGrid = grid.map((r) => r.slice());
  
      if (showHighlightOnly) {
        // Highlight only
        setHighlightCoord({ row: initialRow, col: initialCol });
        setDestinationCoord({ row: newRow, col: newCol });
        setShowHighlightOnly(false);
        setCurrentMoveIndex(nextMoveIndex);
      } else {
        // Perform the move
        const initCell = updatedGrid[8 - initialRow][initialCol - 1];
        const newPos = `${newRow < 10 ? "0" : ""}${newRow},${newCol < 10 ? "0" : ""}${newCol}`;
        const movedContainer = {
          ...initCell,
          position: newPos
        };
  
        updatedGrid[8 - newRow][newCol - 1] = movedContainer;
        updatedGrid[8 - initialRow][initialCol - 1] = {
          position: initCell.position,
          weight: "00000",
          status: "UNUSED"
        };
  
        setGrid(updatedGrid);
        setShowHighlightOnly(true);
  
        // Log the movement
        // Assuming `movedContainer.status` holds the container's commodity/status
        try {
          const logMessage = `${movedContainer.status} moved to (${newPos}) for balance`;
          const logResponse = await fetch("http://127.0.0.1:5000/api/log_action", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: logMessage })
          });
  
          if (!logResponse.ok) {
            console.error("Failed to log ship movement");
          }
        } catch (err) {
          console.error("Error logging movement:", err);
        }
  
        // currentMoveIndex was incremented in the highlight phase already
      }
    }
  };

  useEffect(() => {
    // If we finished all moves, clear highlights
    if (moves.length > 0 && currentMoveIndex >= moves.length - 1 && showHighlightOnly) {
      // At this point we've done the highlight and move for all moves
      setHighlightCoord(null);
      setDestinationCoord(null);
    }
  }, [currentMoveIndex, moves, showHighlightOnly]);

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = async (confirm) => {
    setOpenDialog(false);
    if (confirm) {
      try {
        const response = await fetch("http://127.0.0.1:5000/api/finalize_balance", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(grid)
        });

        if (!response.ok) {
          throw new Error("Failed to finalize balance on the server.");
        }

        router.push("/main");
        sessionStorage.removeItem("operation")
      } catch (err) {
        console.error(err);
        alert("Error finalizing balance: " + err.message);
      }
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", flexDirection: "column" }}>
        <Typography variant="h6" color="error">
          {error}
        </Typography>
      </Box>
    );
  }

  const isBeforeFirstMove = currentMoveIndex === -1 && showHighlightOnly;
  const allMovesDone = currentMoveIndex >= moves.length - 1 && showHighlightOnly && moves.length > 0;

  return (
    <div>
      <MenuBar />
      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", mt: 2 }}>
        {!allMovesDone ? (
          <Button variant="contained" onClick={handleNext}>
            {isBeforeFirstMove ? "Begin Balance" : "Next"}
          </Button>
        ) : (
          <>
            <Typography variant="h4">
              <Alert severity="success">Balancing is Complete!</Alert>
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Button variant="contained" color="primary" onClick={handleOpenDialog}>
                Complete Balance
              </Button>
            </Box>
          </>
        )}
      </Box>

      <Dialog open={openDialog} onClose={() => handleCloseDialog(false)}>
        <DialogTitle>{"Send Outbound Manifest"}</DialogTitle>
        <DialogActions>
          <Button onClick={() => handleCloseDialog(true)} color="primary" autoFocus>
            OK
          </Button>
        </DialogActions>
      </Dialog>

      <Box sx={{ position: "relative", width: "fit-content", margin: "0 auto", mt: 4 }}>
        <Box sx={{ position: "absolute", left: "-260px", top: "0" }}>
          <Card sx={{ width: 250 }}>
            <CardContent>
              <Typography variant="h6" component="div" gutterBottom>
                Est. Time of Completion
              </Typography>
              <Typography variant="h6" style={{justifyContent: "center"}}>{time}</Typography>
            </CardContent>
          </Card>
        </Box>

        <GridDisplay
          grid={grid}
          highlightCoord={highlightCoord}
          destinationCoord={destinationCoord}
        />
      </Box>

      <CommentButton />
    </div>
  );
}
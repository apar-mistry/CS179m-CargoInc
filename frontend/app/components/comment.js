import React, { useState } from "react";
import { Fab, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import axios from "axios";
const CommentButton = () => {
  const [open, setOpen] = useState(false);
  const [comment, setComment] = useState("");

  const handleOpenDialog = () => {
    setOpen(true);
  };

  const handleCloseDialog = () => {
    setOpen(false);
    setComment(""); // Reset the form field
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://127.0.0.1:5000/api/log_operator', { log: comment, username: sessionStorage.getItem("username") });
      
    } catch (error) {
      console.error('Error logging in:', error);
    }
    handleCloseDialog();
  };

  return (
    <>
      <Fab
        style={{ backgroundColor: "var(--warning-yellow)" }}
        aria-label="edit"
        sx={{
          position: "fixed",
          bottom: 16,
          left: 16,
        }}
        onClick={handleOpenDialog}
      >
        <EditIcon sx={{ color: "white"  }}  />
      </Fab>

      <Dialog open={open} onClose={handleCloseDialog}>
        <DialogTitle>Add a Comment</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Comment"
            type="text"
            fullWidth
            variant="outlined"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSubmit} color="primary" variant="contained">
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default CommentButton;
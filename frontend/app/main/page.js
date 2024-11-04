"use client";
import React, { useEffect, useState } from "react";
import {
  Button,
  Container,
  Typography,
  Box,
  Grid2,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { useRouter } from "next/navigation";
import axios from "axios";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";

const MainPage = () => {
  const [username, setUsername] = useState("");
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [operation, setOperation] = useState("");
  const router = useRouter();

  useEffect(() => {
    const storedUsername = sessionStorage.getItem("username");
    if (storedUsername) {
      setUsername(storedUsername);
    } else {
      router.push("/"); // Redirect to login if no username is found
    }
  }, [router]);

  const handleLogout = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://127.0.0.1:5000/api/log_logout", {
        username: username,
      });
      sessionStorage.setItem("username", "");
      router.push("/"); // Redirect to the main page after login
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  const handleOpenDialog = (operationType) => {
    setOperation(operationType);
    setOpen(true);
  };

  const handleCloseDialog = () => {
    setOpen(false);
    setFile(null); // Clear file input on close
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === "text/plain") {
      setFile(selectedFile);
    } else {
      alert("Please select a .txt file.");
    }
  };

  const handleUpload = () => {
    if (file) {
      // Here you can add the logic to upload the file
      console.log(`Uploading ${file.name} for ${operation} operation.`);
      // Close the dialog after the upload action
      handleCloseDialog();
    } else {
      alert("Please select a .txt file.");
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ backgroundColor: "var(--steel-gray)" }}>
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="logo"
            sx={{ mr: 2 }}
          >
            <img
              src="/crane.png" // Replace with your image path or URL
              alt="Logo"
              style={{ width: "40px", height: "40px" }}
            />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Welcome, {username}!
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" style={{ marginTop: "50px" }}>
        <Grid2 container direction="column" alignItems="center" spacing={3}>
          <Grid2 item>
            <Typography variant="h4" component="h1" align="center">
              Which operation would you like to complete?
            </Typography>
          </Grid2>

          {/* Logo */}
          <Grid2 item>
            <img
              src="/logo.png" // Replace with your logo path
              alt="Logo"
              style={{ width: "200px", height: "auto" }}
            />
          </Grid2>

          {/* Buttons */}
          <Grid2 item container justifyContent="center" spacing={2}>
            <Grid2 item>
              <Button
                variant="contained"
                size="large"
                onClick={() => handleOpenDialog("Balancing")}
                sx={{ backgroundColor: "var(--dock-blue)" }}
              >
                Balance
              </Button>
            </Grid2>
            <Grid2 item>
              <Button
                variant="contained"
                size="large"
                onClick={() => handleOpenDialog("Load/Unload")}
                sx={{ backgroundColor: "var(--safety-orange)" }}
              >
                Load/Unload
              </Button>
            </Grid2>
          </Grid2>
        </Grid2>
      </Container>

      <Dialog open={open} onClose={handleCloseDialog}>
        <DialogTitle>Upload File for {operation}</DialogTitle>
        <DialogContent>
          <input type="file" accept=".txt" onChange={handleFileChange} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleUpload} color="primary">
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MainPage;

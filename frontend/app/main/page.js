"use client";
import React, { useEffect, useState } from "react";
import {
  Button,
  Container,
  Typography,
  Box,
  Grid,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  AppBar,
  Toolbar,
  IconButton
} from "@mui/material";
import { useRouter } from "next/navigation";
import axios from "axios";

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
      await axios.post("http://127.0.0.1:5000/api/log_logout", { username });
      sessionStorage.setItem("username", "");
      router.push("/"); // Redirect to the login page after logout
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

  const handleUpload = async () => {
    if (file) {
      try {
        const formData = new FormData();
        formData.append("file", file);
  
        // Send the file to the backend
        const response = await axios.post("http://127.0.0.1:5000/api/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
  
        console.log("File uploaded successfully:", response.data);
        alert("File uploaded successfully");
  
        // Navigate to the grid display page after successful upload
        router.push("/grid-display");
        handleCloseDialog(); // Close dialog after successful upload
      } catch (error) {
        console.error("Error uploading file:", error);
        alert("Error uploading file");
      }
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
        <Grid container direction="column" alignItems="center" spacing={3}>
          <Grid item>
            <Typography variant="h4" component="h1" align="center">
              Which operation would you like to complete?
            </Typography>
          </Grid>

          <Grid item>
            <img
              src="/logo.png" // Replace with your logo path
              alt="Logo"
              style={{ width: "200px", height: "auto" }}
            />
          </Grid>

          <Grid item container justifyContent="center" spacing={2}>
            <Grid item>
              <Button
                variant="contained"
                size="large"
                onClick={() => handleOpenDialog("Balancing")}
                sx={{ backgroundColor: "var(--dock-blue)" }}
              >
                Balance
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                size="large"
                onClick={() => handleOpenDialog("Load/Unload")}
                sx={{ backgroundColor: "var(--safety-orange)" }}
              >
                Load/Unload
              </Button>
            </Grid>
          </Grid>
        </Grid>
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
import React, { useState, useEffect, Component } from "react";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import Link from "@mui/material/Link";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import Card from "@mui/material/Card";
import CardMedia from "@mui/material/CardMedia";
import "./App.css";

const theme = createTheme();

function Copyright(props) {
  return (
    <Typography
      variant="body2"
      color="text.secondary"
      align="center"
      {...props}
    >
      {"Copyright © "}
      <Link color="inherit" href="https://idodo.dev">
        Ido Avraham
      </Link>{" "}
      {new Date().getFullYear()}
      {"."}
    </Typography>
  );
}

class App extends Component {
  state = {
    pathToReport: "static/instructions.jpg",
  };

  handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    const formdata = {
      orders1: data.get("orders1"),
      orders2: data.get("orders2"),
      orders3: data.get("orders3"),
      orders4: data.get("orders4"),
      orders5: data.get("orders5"),
      orders6: data.get("orders6"),
      orders7: data.get("orders7"),
      orders8: data.get("orders8"),
    };

    console.log(formdata);

    const requestOptions = {
      method: "POST",
      body: JSON.stringify(formdata),
      headers: { 'Content-Type': 'application/json' }
    };

    fetch("api/report", requestOptions)
      .then((res) => res.json())
      .then((data) => {
        this.setState({
          pathToReport: "reports/" + data.guid + ".png",
        });
        console.log(this.state);
      });
  };

  render() {
    const { pathToReport } = this.state.pathToReport;

    return (
      <ThemeProvider theme={theme}>
        <Container component="main">
          <CssBaseline />

          <AppBar position="absolute" color="default">
            <Toolbar>
              <Typography variant="h5" color="inherit" noWrap>
                Wolt 2021 recap
              </Typography>
            </Toolbar>
          </AppBar>

          <Box
            sx={{
              marginTop: 10,
              display: "flex",
              flexDirection: "column",
              alignItems: "left",
            }}
          >
            <Typography variant="h5" alignItems="left" color="inherit" noWrap>
              Instructions:
            </Typography>
            <Typography variant="h8" alignItems="left" color="inherit" noWrap>
              <ol>
                <li>
                  Browse the{" "}
                  <a href="https://wolt.com" target="_blank">
                    wolt.com
                  </a>{" "}
                  site with Google Chrome.
                </li>
                <li>
                  Open developer tools (F12) and switch to the network tab.
                </li>
                <li>Filter requests by the word "order_details".</li>
                <li>Login and go to Profile-&gt;Order History</li>
                <li>
                  Paste your response JSONs for the order Requests in the form
                  below.
                </li>
                <ul>
                  <li>Make sure you load all order pages for 2021</li>
                  <li>
                    You can add orders from several diffrerent people to get one
                    combined report
                  </li>
                </ul>
                <li>That's it! Submit the form and receive your report.</li>
              </ol>
            </Typography>
          </Box>

          <Container component="form" noValidate onSubmit={this.handleSubmit}>
            <Grid container spacing={1}>
              <Grid item>
                <TextField fullWidth label="Paste orders JSON" name="orders1" />
              </Grid>
              <Grid item>
                <TextField fullWidth label="Paste orders JSON" name="orders2" />
              </Grid>
              <Grid item>
                <TextField fullWidth label="Paste orders JSON" name="orders3" />
              </Grid>
              <Grid item>
                <TextField fullWidth label="Paste orders JSON" name="orders4" />
              </Grid>
              <Grid item>
                <TextField fullWidth label="Paste orders JSON" name="orders5" />
              </Grid>
              <Grid item>
                <TextField fullWidth label="Paste orders JSON" name="orders6" />
              </Grid>
              <Grid item>
                <TextField fullWidth label="Paste orders JSON" name="orders7" />
              </Grid>
              <Grid item>
                <TextField fullWidth label="Paste orders JSON" name="orders8" />
              </Grid>
            </Grid>

            <Button type="submit" fullWidth variant="contained">
              Submit!
            </Button>

            <Card>
              <CardMedia component="img" image={this.state.pathToReport} />
            </Card>
          </Container>

          <Copyright sx={{ mt: 5 }} />
        </Container>
      </ThemeProvider>
    );
  }
}

export default App;

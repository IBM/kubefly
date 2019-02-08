/* jshint esversion: 6 */

// kube client
const { Client, config } = require('kubernetes-client');
const utils = require('./utils');
let client = utils.initKubeClient(Client, config);

// server
const express = require('express');
const app = express();
const net = require('net');

let mySocket = null;
const namespace = 'default';

//global variables
MAX_X = 2.89
MAX_Y = 2.29
MAX_Z = 2.3
MAX_DRONES = 4 // DO NOT CHANGE.

ENABLELIGHTBOXES = false;
drones = []
lightBoxes = [];
// get the current pods, and update data
const queryPods = () => {
  console.log('>queryPods');
  client.api.v1.namespaces(namespace).pods.get().then((pods) => {
    utils.assignPodsToDrones(pods);
    utils.removeDeletedPods(pods);
    console.log(drones);
  }).catch((e) => console.log(e));
  console.log('<queryPods');
}

const queryWorkerNodes = () => {
  console.log('>queryWorkerNodes');
  client.api.v1.nodes().get().then((nodes) => {
    workernodes = nodes.body.items;
    utils.assignWorkerNodesToLights();
  }).catch((e) => console.log(e));
  console.log('<queryWorkerNodes');
}

app.get('/', function (req, res) {
  res.json(drones)
})

app.get('/B', function (req, res) {
  console.log('ENABLELIGHTBOXES');
  ENABLELIGHTBOXES = true;
  res.send("OK")
})
app.get('/dead-drone/:id', function (req, res) {
  console.log('/dead-drone/${req.params.id}');
  for (drone of drones) {
    if (drone.droneId == req.params.id && drone.podName) {
      client.api.v1.namespaces('default').pods(drone.podName).delete({ qs: { gracePeriodSeconds: 0 } })
      res.json({ message: `Deleted ${drone.podName}` });
      console.log(`Deleted ${drone.podName}`);
      return;
    }
  }
  console.log(`Deleted failed`);
  res.json({ message: `Delete failed` });
})

// express app listing to any service connection on port 3000
const port = 3000;
app.listen(port, () => {
  console.log("Your app is running on port: " + port);
  drones = utils.getInitialPositions();
  lightBoxes = utils.initLightsBoxes(3);
  queryWorkerNodes();
  setInterval(queryPods, 3000);
});

module.exports = app;

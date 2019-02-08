/* jshint esversion: 6 */
// check if podName is in pods array
module.exports = {
  // Initial json of all the drones
  // Used to reset unassigned drones later
  getInitialPositions() {
    var homePositions = []
    for (let i = 0; i < MAX_DRONES; i++) {
      var location, color;
      var midPoint = Math.round(MAX_DRONES / 2) - 1;
      if (i <= midPoint) { //first half of drones go in front
        location = {
          x: (MAX_X / 3) * (i + 1),
          y: MAX_Y / 5,
          z: 0
        }
      } else { //others go in the back
        location = {
          x: (MAX_X / 3) * (i - midPoint),
          y: MAX_Y * 2 / 4,
          z: 0
        }
      }
      var color = white
      homePositions.push({
        droneId: i,
        podName: null,
        location,
        color
      });
    }
    return homePositions;
  },
  assignPodsToDrones(pods) {
    console.log(">assignPodsToDrones");
    // go through each running pod
    for (var runningPod of pods.body.items) {
      podName = runningPod.metadata.name;
      if (this.indexOfPodinDrones(podName) == -1) { // new pod
        const freeDroneIndex = this.getFreeDroneIndex();
        if (freeDroneIndex > -1) {
          this.assignDrone(freeDroneIndex, podName);
        } else {
          console.log("ERROR! NO MORE FREE DRONES FOUND!")
          continue;
        }
      }
      this.updateDroneStatus(runningPod);
    }
    console.log("<assignPodsToDrones");
  },
  assignDrone(freeDroneIndex, podName) {
    console.log(`assignAndTakeOffDrone(${freeDroneIndex})`)
    drones[freeDroneIndex].podName = podName;
    drones[freeDroneIndex].location.z = 1;
  },
  updateDroneStatus(runningPod) {
    console.log(`${runningPod.metadata.name} is ${runningPod.status.phase}`);
    var indexOfPod = this.indexOfPodinDrones(podName)
    if (runningPod.status.phase == 'Running') {
      drones[indexOfPod].location.z = 1;
      if (ENABLELIGHTBOXES) {
        this.moveDroneToLightBox(indexOfPod, runningPod);
      } else {
        drones[indexOfPod].color = blue;
      }
    } else if (runningPod.status.phase == 'Pending') {
      if (ENABLELIGHTBOXES) {
        drones[indexOfPod].color = yellow;
        drones[indexOfPod].location.y = MAX_Y / 2.0
        drones[indexOfPod].location.x = Math.random() * MAX_X
      } else {
        drones[indexOfPod].color = blue;
      }
      drones[indexOfPod].location.z = 0.75;
    } else if (runningPod.status.phase == 'Terminating') {
      landAndResetDrone(indexOfPod);
    }
  },
  moveDroneToLightBox(freeDroneIndex, runningPod) {
    let podWorkerNode = runningPod.spec.nodeName;
    if (!podWorkerNode) {
      console.log(`${runningPod.metadata.name} has no worker node.`)
      return;
    }
    let lightBox = this.getLightBoxForNode(podWorkerNode)
    drones[freeDroneIndex].location.x = lightBox.location.x;
    drones[freeDroneIndex].location.y = lightBox.location.y;
    drones[freeDroneIndex].color = lightBox.color;
  },
  getLightBoxForNode(podWorkerNode) {
    console.log("getLightBoxForNode: " + podWorkerNode);
    for (lightBox of lightBoxes) {
      if (lightBox.workerNode == podWorkerNode) {
        return lightBox
      }
    }
  },
  getFreeDroneIndex() {
    for (let j = 0; j < drones.length; j++) {
      if (drones[j].podName == null) {
        return j
      }
    }
    return -1;
  },
  indexOfPodinDrones(podName) {
    for (let j = 0; j < drones.length; j++) {
      if (drones[j].podName === podName) {
        return j
      }
    }
    return -1
  },
  landAndResetDrone(resetDroneIndex) {
    console.log(`>landAndResetDrone with index ${resetDroneIndex}`)
    var initialPositions = this.getInitialPositions();
    drones[resetDroneIndex] = initialPositions[drones[resetDroneIndex].droneId]
    //move this drone to the back of the array so it doesn't get reassigned immediately
    drones.push(drones.splice(resetDroneIndex, 1)[0]);

  },
  getRunningPods(pods) {
    const runningPods = [];
    for (let i = 0; i < pods.body.items.length; i++) {
      const { phase } = pods.body.items[i].status;
      if (phase === 'Running' || phase === 'ContainerCreating' || phase === 'Pending') {
        runningPods.push(pods.body.items[i]);
      }
    }
    return runningPods;
  },
  removeDeletedPods(pods) {
    console.log(">removeDeletedPods")
    const runningPods = this.getRunningPods(pods);
    var runningPodNames = [];
    for (runningPod of runningPods) {
      runningPodNames.push(runningPod.metadata.name)
    }
    for (let j = 0; j < drones.length; j++) {
      if (drones[j].podName != null && !runningPodNames.includes(drones[j].podName)) { // a drone is assigned to a pod that isn't running anymore
        this.landAndResetDrone(j)
        if (ENABLELIGHTBOXES) {
          return; // For B scenarios, only land 1 node at a time to avoid collisions
        }
      }
    }
    console.log("<removeDeletedPods");
  },
  initKubeClient(Client, config) {
    try {
      client = new Client({
        config: config.fromKubeconfig(),
        version: '1.9',
      });
    } catch (err) {
      try {
        client = new Client({
          config: config.getInCluster(),
        });
        client.loadSpec();
      } catch (error) {
        console.error('Can\'t connect to Kube API, did you set your $KUBECONFIG?');
        process.kill();
      }
    }
    return client;
  },
  // blue, green and purple
  initLightsBoxes(numLightBoxes) {
    console.log(`initAvailableLightsBoxes(${numLightBoxes})`);
    const lights = [];
    var color;
    for (let i = 0; i < numLightBoxes; i++) {
      switch (i) {
        case 0:
          color = red;
          break;
        case 1:
          color = blue;
          break;
        case 2:
          color = green;
          break;
      }
      lights.push({
        lightBoxesId: i,
        location: {
          x: (MAX_X / 4) * (i + 1),
          y: MAX_Y * 4 / 5,
        },
        color
      });
    }
    console.log(lights);
    return lights;
  },
  assignWorkerNodesToLights() {
    for (i in workernodes) {
      lightBoxes[i].workerNode = workernodes[i].metadata.name;
    }
    console.log(lightBoxes)
  },
};
getColorJSON = (r, g, b) => {
  return { r, g, b }
}

red = getColorJSON(255, 0, 0);
green = getColorJSON(0, 255, 0);
blue = getColorJSON(0, 0, 255);
yellow = getColorJSON(255, 255, 0);
white = getColorJSON(255, 255, 255);


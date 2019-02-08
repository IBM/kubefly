
# **Kubefly** - Understanding Kubernetes using Drones

Kubernetes is one of the fastest-growing technologies in the industry, and for good reason. Kubernetes provides an isolated and secure app platform for managing containers - ultimately transforming application development and operations for your team or company. You may have heard, or felt, that Kubernetes is complex or hard to learn. 

Kubefly was born out of a simple idea, explain the concepts of Kubernetes, Istio and cloud native technologies in a few and visual way.  We wanted to help people understand what was going on behind the scenes.  

The question was how to visualize the concepts?  

The answer was **Drones!!**

Our team at IBM recently built a demo to teach and demonstrate core Kubernetes concepts using a swarm of flying drones. The drones showcase concepts like pods, replica sets, deployments, and stateful sets.  Once you apply your Kubernetes Deployment describing an application, you'll see a few drones take off -- each one representing a pod in the deployment. If one of the kubernetes pods is killed, you'll see the drone land, and another will take its place, as Kubernetes' declarative model will always attempt to match the desired state.

This project will share the demo code we built and the equipment that we used.

# The Gear
To build the demo we used drones from  [Bitcraze.io](https://www.bitcraze.io). The drones are [Crazyflie 2.0](https://www.bitcraze.io/crazyflie-2/) drones. ![Crazyflie](https://www.bitcraze.io/images/Crazyflie2.0/Crazyflie2.0-585px.JPG) 

These are open source drones that have a rich API and easy to use programming libraries. And the really cool part is they are extensible with a set of add-on decks. For our demo we used the [LED Ring Deck](https://www.bitcraze.io/led-ring-deck/) to provide the lights on the bottom of the drones.

![LED Ring Deck](https://www.bitcraze.io/images/led-ring/ledring-side.jpg)

To do positioning, we used the [Loco Positioning System](https://www.bitcraze.io/loco-pos-system/). LPS is essentially indoor GPS and allows the drones to fly autonomously and gives us an API to tell them an exact coordinate we want them to fly to.  ![LPS](https://www.bitcraze.io/images/loco-pos-deck/locoPositioning_deck_585px_side.JPG).

In our case we actually bought the [Swarm Bundle](https://store.bitcraze.io/collections/bundles/products/the-swarm-bundle), which provided 10 drones, the Loco Positoning System, and all the parts we needed. 

If you want to start small, you can play with a single Crazyflie drone and the [Flow Deck](https://www.bitcraze.io/flow-deck-v2/). This will allow you to do similar things without the complexing of the full LPS. 

# The Software
Kubefly is made up of two key components, the **Drone Controller** and the **Kubernetes Watcher**.

## Drone Controller
The Drone controller, in the [drone-controller](/drone-controller) folder, is a python program that runs on your laptop and connects via radio link directly to the drones. Drone controller also connects to a Kubernetes cluster running in the cloud. In our case we ran Kubernetes on [IBM Cloud](https://cloud.ibm.com) using [IBM Cloud Kubernetes Service (IKS)](http://ibm.com/iks). Drone controller is basically the link between the cloud and the drones to enable commands to be sent back and forth.

## Kubernetes Watcher
The Kubernetes Watcher, in the [kube-watcher](/kube-watcher) folder, is a Go program that runs inside Kubernetes. It watches the Kube API server for, events such as Pods starting and stopping, and translates those events into commands for the drones sent to the drone connection. 

## MyApp
MyApp, in the [myapp](/myapp) folder, is a simple demo application you can run on Kubernetes to test things out.

# How to Guide
TODO - We will provide step by step instructions on how to run Kubefly soon :) 

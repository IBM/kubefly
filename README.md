
# **Kubefly** - Understanding Kubernetes using Drones

Kubernetes is one of the fastest-growing technologies in the industry, and for good reason. Kubernetes provides an isolated and secure app platform for managing containers - ultimately transforming application development and operations for your team or company. You may have heard, or felt, that Kubernetes is complex or hard to learn. 

Kubefly was born out of a simple idea, explain the concepts of Kubernetes, Istio and cloud native technologies in a fun and visual way. We wanted to help people understand what was going on behind the scenes. 

The question was how to visualize the concepts?  

The answer was **Drones!!**

Our team at IBM recently built a demo to teach and demonstrate core Kubernetes concepts using a swarm of flying drones. The drones showcase concepts like pods, replica sets, deployments, and stateful sets.  Once you apply your Kubernetes Deployment describing an application, you'll see a few drones take off -- each one representing a pod in the deployment. If one of the kubernetes pods is killed, you'll see the drone land, and another will take its place, as Kubernetes' declarative model will always attempt to match the desired state.

This project will share the demo code we built and the equipment that we used.

# The Gear
To build the demo we used drones from  [Bitcraze.io](https://www.bitcraze.io). The drones are [Crazyflie 2.0](https://www.bitcraze.io/crazyflie-2/) drones. ![Crazyflie](https://www.bitcraze.io/images/Crazyflie2.0/Crazyflie2.0-585px.JPG) 

These are open source drones that have a rich API and easy to use programming libraries. And the really cool part is that they are extensible with a set of add-on decks. For our demo we used the [LED Ring Deck](https://www.bitcraze.io/led-ring-deck/) to provide the lights on the bottom of the drones.

![LED Ring Deck](https://www.bitcraze.io/images/led-ring/ledring-side.jpg)

To position the drones, we used the [Loco Positioning System](https://www.bitcraze.io/loco-pos-system/). LPS is essentially indoor GPS, allowing the drones to fly autonomously. LPS also provides an API to tell the drones an exact coordinate we want them to fly to.  ![LPS](https://www.bitcraze.io/images/loco-pos-deck/locoPositioning_deck_585px_side.JPG).

In our case we actually bought the [Swarm Bundle](https://store.bitcraze.io/collections/bundles/products/the-swarm-bundle), which provided 10 drones, the Loco Positoning System, and all the parts we needed. 

If you want to start small, you can play with a single Crazyflie drone and the [Flow Deck](https://www.bitcraze.io/flow-deck-v2/). This will allow you to do similar things without the complexity of the full LPS. 

# The Software
Kubefly is made up of two key components, the **Drone Controller** and the **Kubernetes Watcher**.

## Drone Controller
The Drone controller, in the [drone-controller](/drone-controller) folder, is a python program that runs on your laptop and connects via radio link directly to the drones. Drone controller will call the kube-watcher API to recieve data about where the drones should be positioned, and then will send commands to the drones based on that data. 

## Kubernetes Watcher
The Kubernetes Watcher, in the [kube-watcher](/kube-watcher) folder, is a Node.js program that runs locally, on your laptop. It uses the Kubernetes API to connect to a Kubernetes cluster and watches for events such as Pods starting and stopping. Kube-watcher then translates those events into positions for the drones sent to the drone connection. In our case we ran Kubernetes on [IBM Cloud](https://cloud.ibm.com) using [IBM Cloud Kubernetes Service (IKS)](http://ibm.com/iks).

## MyApp
MyApp, in the [myapp](/myapp) folder, is a simple demo application you can run on Kubernetes to test things out.

# How to Guide
TODO - We will provide step by step instructions on how to run Kubefly soon :) 

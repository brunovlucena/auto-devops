# auto-devops: Your K8s Cluster Co-Pilot 🤖✨

## 🌟 Why auto-devops?

* **Faster Incident Resolution:** By providing immediate context and enabling quick, secure actions, auto-devops significantly reduces Mean Time To Resolution (MTTR).
* **Enhanced Operational Efficiency:** Automate routine checks, gather data, and execute commands with voice or a simple tap.
* **Improved Engineer Experience:** Reduce the cognitive load on engineers during stressful situations by providing a smart, interactive assistant.
* **Secure by Design:** With features like facial recognition for command execution, auto-devops prioritizes the security of your cluster.
* **Extensible & Adaptable:** Integrate auto-devops with your existing toolchain and custom solutions.
* **Reports**
* **AnomalyDetection**

---

## 🔮 The Vision

auto-devops aims to be an indispensable member of your DevOps team, learning and evolving to provide increasingly sophisticated support for managing complex Kubernetes environments.

---

## 🛠️ Getting Started

### Prerequisites

* Kubernetes cluster (v1.32+)
* [kubectl](https://kubernetes.io/docs/tasks/tools/) installed and configured
* [Pulumi](https://www.pulumi.com/docs/install/) installed
* [Go](https://golang.org/doc/install) (v1.24+)
* [ArgoCD CLI](https://argo-cd.readthedocs.io/en/stable/cli_installation/) (optional, for advanced management)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/brunovlucena/auto-devops.git
   cd auto-devops
   ```

2. Bootstrap the environment:
   ```
   cd 40-bootstrap
   pulumi up --stack local
   ```

3. Access the auto-devops dashboard:
   Once deployed, you can access the auto-devops dashboard through the provided URL in the installation output.

### Architecture

auto-devops consists of several key components:

- Kind
- K8s
- Observability (Loki, Tempo, Alloy, Prometheus)
- Opik
- MongoDb (Vector DB)
- Llamma 4 (MCP Server, Go)
- Pulumi (Go/IaC)
- ArgoCD MCP server
- Grafana MCP server 
- GitHub MCP server
- MongoDB MCP Server
- Cursor MCP Client (text)
- KubeVox
- Linkerd
- LangGraph
- Langchain
- FastAPI
- Websocket
- nektos/act

---

## 📱 Mobile App

The auto-devops mobile app is available for both iOS and Android, enabling:

* Push notifications for critical alerts
* Secure command execution with facial recognition
* Voice-activated cluster querying
* Monitoring dashboard access

Note: This is a vision. *Mobile app download links will be available in my lifetime.*

---

## 🤝 Contributing

auto-devops is an open-source project and we welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please see our [Contributing Guide](00-docs/CONTRIBUTING.md) for more details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

Project Maintainers - [bruno@lucena.cloud](mailto:bruno@lucena.cloud)
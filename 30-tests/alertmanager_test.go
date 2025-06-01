package main

import (
	"os/exec"
	"strings"
	"testing"

	"gopkg.in/yaml.v2"
)

type Config struct {
	Receivers []struct {
		Name         string `yaml:"name"`
		SlackConfigs []struct {
			APIURL string `yaml:"api_url"`
		} `yaml:"slack_configs"`
	} `yaml:"receivers"`
}

func TestAlertmanagerConfig(t *testing.T) {
	pod := "alertmanager-prometheus-kube-prometheus-alertmanager-0"
	namespace := "prometheus"
	path := "/etc/alertmanager/config_out/alertmanager.env.yaml"

	// exec into the pod and read the config file
	cmd := exec.Command("kubectl", "exec", "-n", namespace, pod, "--", "cat", path)
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("Failed to read config file: %v\n%s", err, string(output))
	}

	var cfg Config
	if err := yaml.Unmarshal(output, &cfg); err != nil {
		t.Fatalf("Failed to parse YAML: %v", err)
	}

	found := false
	for _, r := range cfg.Receivers {
		if r.Name == "notifi-notifications-dev" {
			for _, slack := range r.SlackConfigs {
				if strings.Contains(slack.APIURL, "https://hooks.slack.com/services/") {
					t.Logf("Found expected API URL: %s", slack.APIURL)
					found = true
				}
			}
		}
	}

	if !found {
		t.Fatalf("Expected Slack webhook URL not found in config")
	}
}

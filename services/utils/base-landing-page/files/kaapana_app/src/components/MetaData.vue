<template>
  <v-card elevation="0" style="min-height: 100%">
    <v-card-title>
      <v-container align-items="center">
        <v-row align="center" justify="center">
          <v-col>
            <v-row align="center" justify="center">
              Patients
            </v-row>
            <v-row align="center" justify="center">
              {{ this.metrics['Patients'] || 'N/A' }}
            </v-row>
          </v-col>
          <v-col>
            <v-row align="center" justify="center">
              Studies
            </v-row>
            <v-row align="center" justify="center">
              {{ this.metrics['Studies'] || 'N/A' }}
            </v-row>
          </v-col>
          <v-col>
            <v-row align="center" justify="center">
              Series
            </v-row>
            <v-row align="center" justify="center">
              {{
                this.metrics['Series'] || 'N/A'
              }}
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-card-title>

    <v-card-text>
      <apexcharts
          v-for="[key, values] in Object.entries(this.histograms)"
          :key="JSON.stringify({key: values})"
          :options="{
            chart: {
              id: key,
              events: {
                dataPointSelection: (event, chartContext, config) => {
                  return dataPointSelection(event, chartContext, config, key, values)
                },
              },
              toolbar: {
                show: true,
                offsetX: 0,
                offsetY: 0,
                tools: {
                  download: true,
                  selection: true,
                  zoom: true,
                  zoomin: true,
                  zoomout: true,
                  pan: true,
                  reset: true,
                  //customIcons: []
                },
                export: {
                  csv: {
                    filename: undefined,
                    columnDelimiter: ',',
                    headerCategory: 'category',
                    headerValue: 'value',
                    dateFormatter(timestamp) {
                      return new Date(timestamp).toDateString()
                    }
                  },
                  svg: {
                    filename: undefined,
                  },
                  png: {
                    filename: undefined,
                  }
                },
                autoSelected: 'zoom'
              },
            },
            title: {
              text: key,
            },
            xaxis: {
              categories: Object.keys(values['items']),
              tickPlacement: 'on'
            }
          }"
          :series="[{
            name: key,
            data: Object.values(values['items'])
          }]"
          type="bar"
      >
      </apexcharts>
    </v-card-text>
  </v-card>
</template>

<script>
/* eslint-disable */
import VueApexCharts from "vue-apexcharts";
import {loadDashboard} from "@/common/api.service";
import {settings} from "@/static/defaultUIConfig";


export default {
  name: 'MetaData',
  components: {
    apexcharts: VueApexCharts,
  },
  props: {
    seriesInstanceUIDs: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      histograms: {},
      metrics: {},
      fields: [],
      settings: settings
    }
  },
  created() {
    this.settings = JSON.parse(localStorage['settings'])
    this.fields = this.settings.datasets.props.filter(i => i.dashboard).map(i => i.name)
  },
  watch: {
    seriesInstanceUIDs() {
      this.updateDashboard()
    }
  },
  mounted() {
    this.updateDashboard()
  },
  methods: {
    updateDashboard() {
      loadDashboard(this.seriesInstanceUIDs, this.fields).then(data => {
        this.histograms = data['histograms'] || {}
        this.metrics = data['metrics'] || {}
      })
    },
    dataPointSelection(event, chartContext, config, key, value) {
      console.log(Object.keys(value['items']), config['dataPointIndex'])
      this.$emit(
          'dataPointSelection',
          {
            key: key,
            value: Object.keys(value['items'])[config['dataPointIndex']]
          }
      )
    }
  }
};
</script>
<style scoped>
</style>

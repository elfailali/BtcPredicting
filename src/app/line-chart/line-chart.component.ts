import { Component } from '@angular/core';
import axios from 'axios';
import Chart from 'chart.js/auto';

const API_URL = 'https://api.coingecko.com/api/v3';

@Component({
  selector: 'app-line-chart',
  templateUrl: './line-chart.component.html',
  styleUrls: ['./line-chart.component.css']
})
export class LineChartComponent {
  chart: any;
  

  async createChart() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(endDate.getMonth() - 1);

    console.log("the end;" + endDate)

    const response = await axios.get(`${API_URL}/coins/bitcoin/market_chart`, {
      params: {
        vs_currency: 'usd',
        days: 7,
        interval: 'hourly'
      },
    });
    // example response =
    // https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=7&interval=hourly


    const prices = response.data.prices;
    const timeStamps = prices.map((price: any) => new Date(price[0]));

    // CONVERT timeStamps FROM '' TO 'Apr 26, 2023, 4:01:09 AM'
    let time_stamp = [];
    for(var date of timeStamps){
      time_stamp.push(this.convert_date(date));
    }

    // DEFINE THE LINE CHART
    this.chart = new Chart("MyChart", {
      type: 'line',
      data: {
        labels: time_stamp,
        datasets: [
          {
            label: "Bitcoin Price (USD)",
            data: prices.map((price: any) => price[1]),
            backgroundColor: 'blue'
          }
        ]
      },
      options: {
        aspectRatio: 2
      }
    });
  }

  ngOnInit(): void {
    this.createChart();
  }

  convert_date(date : Date){
    // take date = "Wed Apr 26 2023 04:01:09 GMT+0200 (heure d’été d’Europe centrale)"
    // return Output: Apr 26, 2023, 4:01:09 AM
      const formattedDate = date.toLocaleString("en-US", { 
      year: 'numeric', 
      month: 'short', 
      day: '2-digit', 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      timeZone: 'Europe/Paris'
    });
    return formattedDate;
  }

}

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
    const emptyValue = Array(90).fill(null);
    let n_dates: string[] = [];
    let n_predictions: number[] = [];


    startDate.setMonth(endDate.getMonth() - 1);


    // model api  

    const input =
    {
      "day": 15,
      "month": 5,
      "yesterday_price": 27639,
      "forecast_days": 5
    }


    const response = await axios.get(`${API_URL}/coins/bitcoin/market_chart`, {
      params: {
        vs_currency: 'usd',
        days: 90,
        interval: 'daily'
      },
    });
    await axios.post('http://127.0.0.1:5000/predict', input )
      .then(response => {
        const data = response.data;
        n_dates = data.predictions.map((prediction: { date: string; prediction: number }) => prediction.date);
        n_predictions = data.predictions.map((prediction: { date: string; prediction: number }) => prediction.prediction);
      
      })
      .catch(error => {
        console.error(error.message);
      });



    const newdata = emptyValue.concat(n_predictions);
    const prices = response.data.prices;
    const timeStamps = prices.map((price: any) => new Date(price[0]));

    // CONVERT timeStamps FROM '' TO 'Apr 26, 2023, 4:01:09 AM'
    let time_stamp = [];
    for (var date of timeStamps) {
      time_stamp.push(this.convert_date(date));
      //console.log(typeof this.convert_date(date))
    }
    //(time_stamp:any)=>time_stamp.pop()
    time_stamp=time_stamp.slice(0,-1)

    time_stamp = time_stamp.concat(n_dates)
    
    let  con_data=prices.map((price: any) => price[1])
    con_data=con_data.slice(0,-1)
    console.log(con_data)
    // DEFINE THE LINE CHART
    this.chart = new Chart("MyChart", {
      type: 'line',
      data: {
        labels: time_stamp,
        datasets: [
          {
            // real price plot
            label: "Bitcoin Price (USD)",
            data: con_data,
            backgroundColor: 'blue'
          },
          {
            // predictive price plot
            label: "Predictive Bitcoin Price (USD)",
            // data: prices.map((price: any) => price[1]),
            data: newdata,
            backgroundColor: 'red'
          }
        ],

      },

      options: {
        aspectRatio: 2
      }
    });
  }

  ngOnInit(): void {
    this.createChart();
  }

  convert_date(date: Date) {
    // take date = "Wed Apr 26 2023 04:01:09 GMT+0200 (heure d’été d’Europe centrale)"
    // return Output: Apr 26, 2023, 4:01:09 AM
    const formattedDate = date.toLocaleString("en-US", {
      year: 'numeric',
      month: 'short',
      day: '2-digit'
      //hour: '2-digit', 
      //minute: '2-digit', 
      //second: '2-digit',
      //timeZone: 'Europe/Paris'
    });
    return formattedDate;
  }

}

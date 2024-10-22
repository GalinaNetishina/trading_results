import React, { useEffect, useState } from 'react'
import { TDateProps } from './models';


 function TradingDay({date, handleClick}:TDateProps) {    
  return (
    <div>
       <button className=" btn btn-secondary" onClick={()=>handleClick(`http://127.0.0.1:8000/api/get_dynamics/?limit=10&skip=0&start_date=${date}&end_date=${date}`)} >
        {date}            
        </button> 
    </div>
    
  )
}
  

export default function Dates({handleSource}) {
  const [dates, setDates] = useState<Date[]>([])

  useEffect(()=>{
    const apiUrl = 'http://localhost:8000/api/last_trading_dates/?count=4';
    fetch(apiUrl)
      .then((res) => res.json())
      .then((dates) => 
        setDates(dates))
    }, []);

  return (
    <div className='navbar navbar-dark'>
        <div className="container-fluid justify-content-center gap-3">
        {dates.map((date) => {
            return (
                <TradingDay date={date.date} key={date.date} handleClick={handleSource}/>
            )
        })}
        </div>
    </div>
  )
}

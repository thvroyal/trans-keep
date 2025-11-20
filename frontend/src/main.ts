import './style.css'
import { setupCounter } from './counter.ts'

document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <div>
    <h1>TransKeep</h1>
    <div class="card">
      <button id="counter" type="button">Counter: 0</button>
    </div>
    <p class="read-the-docs">
      Initializing TransKeep Application...
    </p>
  </div>
`

setupCounter(document.querySelector<HTMLButtonElement>('#counter')!)

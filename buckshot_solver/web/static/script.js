var form = document.querySelector('form');
const multiInputPlayer = document.querySelector("multi-input[name='items_player']");
const multiInputDealer = document.querySelector("multi-input[name='items_dealer']");
const submit = document.querySelector("input[type=submit]");
function add_invisible_inputs() {
  var i = 0;
  for (const value of multiInputPlayer.getValues()) {
    var input  = document.createElement('input');
    input.name = 'item_player_' + i;
    input.type = "hidden";
    input.value = value;
    input.onclick = () => {
      multiInputPlayer._deleteItem(item);
    };
    form.appendChild(input);
    i++;
    
  }
  var i = 0;
  for (const value of multiInputDealer.getValues()) {
    input  = document.createElement('input');
    input.name = 'item_dealer_' + i;
    input.type = "hidden";
    input.value = value;
    input.onclick = () => {
      multiInputDealer._deleteItem(item);
    };
    form.appendChild(input);
    i++;
    
  }
    return true;
};
submit.onclick = add_invisible_inputs
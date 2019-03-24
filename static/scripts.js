$(document).ready(function(){
  console.log('here');
  $("defaultOpen").click()
});

$(document).ready(function(){
  console.log('here2');
  $("button").click(function(){
      console.log('clicked: ' + this.name);
      $('.tabcontent').each(function(i, obj) {
           console.log('hide obj: ' + obj.id);
           $('#' + obj.id).hide();
      });
      $('.tablinks').each(function(i, obj) {
           console.log('remove active class from obj: ' + obj.name);
           $( 'button[name=' + this.name + ']' ).removeClass('active');
      });
      $( 'button[name=' + this.name + ']' ).addClass('active');
      $('div[id=' + this.name + ']').show();
  });
});

class Dashing.Linechart extends Dashing.Chartjs
  ready: ->
     @steps = 0
     @chart = @lineChart 'linechart', # The ID of your html element
        []
        [
          label: 'Number of Hosts' # Text displayed when hovered
          colorName: 'blue' # Color of data
          data: [] # Vertical points
        ]
  onData: (data) ->
     @steps++
     if(@chart)
        @chart.addData(
               [data.points[data.points.length-1].y],
               data.points[data.points.length-1].x)

        @chart.removeData() if @steps > 15

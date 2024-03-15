# Snippets for Chapter 7

## <em>Quick links to the recipes</em>
* [Creating alert in Kibana](#creating-alert-in-kibana )


## Creating alert in Kibana
### Alerting message snippet
```
The measured average value is {{context.value}} km/h 

The average vehicle speed for congested locations is less than 12km h over {{rule.params.timeWindowSize}}{rule.params.timeWindowUnit}} 

Timestamp: {{context.date}} 
```

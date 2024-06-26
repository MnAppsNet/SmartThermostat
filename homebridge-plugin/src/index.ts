import axios from "axios";
import {
  AccessoryConfig,
  AccessoryPlugin,
  API,
  CharacteristicEventTypes,
  CharacteristicGetCallback,
  CharacteristicSetCallback,
  CharacteristicValue,
  HAP,
  Logging,
  Service,
} from "homebridge";

let hap: HAP;
export = (api: API) => {
  hap = api.hap;
  api.registerAccessory("smart-thermostat", HTTPThermostat);
};

class HTTPThermostat implements AccessoryPlugin {
  private readonly GetRequiredTemperature = "getRequiredTemperature";
  private readonly GetCurrentTemperature = "getCurrentTemperature";
  private readonly GetCurrentHumidity = "getCurrentHumidity";
  private readonly SetRequiredTemperature = "setRequiredTemperature";

  private readonly log: Logging;
  private readonly name: string;
  private readonly ip: string;
  private readonly serviceURL: string;

  private readonly thermostatService: Service;
  private readonly informationService: Service;

  private temperature = 0;
  private requiredTemperature = 0;
  private humidity = 0;

  private display_units = hap.Characteristic.TemperatureDisplayUnits.CELSIUS;

  constructor(log: Logging, config: AccessoryConfig) {
    this.log = log;
    this.name = config.name;
    this.ip = config.ip;
    this.serviceURL = `http://${this.ip}`;

    // Configure Thermostat Service
    // TargetTemperature
    this.thermostatService = new hap.Service.Thermostat(this.name);
    this.thermostatService
      .getCharacteristic(hap.Characteristic.TargetTemperature)
      .setProps({
        minValue: 0,
        maxValue: 30,
        minStep: 0.1,
      })
      .on(CharacteristicEventTypes.GET, this.getTargetTemperature.bind(this))
      .on(CharacteristicEventTypes.SET, this.setTargetTemperature.bind(this));

    // Current Temperature
    this.thermostatService
      .getCharacteristic(hap.Characteristic.CurrentTemperature)
      .on(CharacteristicEventTypes.GET, this.getTemperature.bind(this));

    // Current Humidity
    this.thermostatService
      .getCharacteristic(hap.Characteristic.CurrentRelativeHumidity)
      .on(CharacteristicEventTypes.GET, this.getHumidity.bind(this));

    // Target Heating Cooling
    this.thermostatService
      .getCharacteristic(hap.Characteristic.CurrentHeatingCoolingState)
      .on(CharacteristicEventTypes.GET, this.getThermostatState.bind(this));

    // Temperature Display Units
    this.thermostatService
      .getCharacteristic(hap.Characteristic.TemperatureDisplayUnits)
      .on(CharacteristicEventTypes.GET, this.getDisplayUnits.bind(this))
      .on(CharacteristicEventTypes.SET, this.setDisplayUnits.bind(this));

    // Configure Information Service
    this.informationService = new hap.Service.AccessoryInformation()
      .setCharacteristic(hap.Characteristic.Manufacturer, "MnApps.NET")
      .setCharacteristic(hap.Characteristic.Model, "smart-thermostat")
      .setCharacteristic(hap.Characteristic.SerialNumber, this.ip);

    log.info("Thermostat finished initializing!");
  }

  getServices(): Service[] {
    return [this.informationService, this.thermostatService];
  }

  private async getThermostatState(
    callback: CharacteristicGetCallback
  ): Promise<void> {
    let state = hap.Characteristic.TargetHeatingCoolingState.OFF;
    try {
      callback(null, state);
    } catch (e) {
      this.log.error(`${e}`);
    }
    try {
      if (this.requiredTemperature > this.temperature) {
        state = hap.Characteristic.TargetHeatingCoolingState.HEAT;
      }
      this.thermostatService
        .getCharacteristic(hap.Characteristic.TargetHeatingCoolingState)
        .updateValue(state);
    } catch (e) {
      this.log.error(`${e}`);
    }
  }

  //Get current humidity
  private async getHumidity(
    callback: CharacteristicGetCallback
  ): Promise<void> {
    // Immediatly respond with potentially stale value
    const old_humidity = this.humidity;
    try {
      callback(null, this.humidity);
    } catch (e) {
      this.log.error(`${e}`);
    }
    try {
      const humidity = await this.getData(this.GetCurrentHumidity);
      if (humidity !== null) {
        this.humidity = humidity;
        this.log.debug(`updated cached humidity: ${this.humidity}`);
      }
    } catch (e) {
      this.log.error(`${e}`);
    } finally {
      // Update Characteristics
      if (old_humidity !== this.humidity) {
        this.thermostatService
          .getCharacteristic(hap.Characteristic.CurrentRelativeHumidity)
          .updateValue(this.humidity);
        this.log.debug(
          `updating characteristic value with cached humidity: ${this.humidity}`
        );
      }
    }
  }

  // Get Current Required Temperature
  private async getTargetTemperature(
    callback: CharacteristicGetCallback
  ): Promise<void> {
    // Immediatly respond with potentially stale value
    const old_temperature = this.requiredTemperature;
    try {
      callback(null, this.requiredTemperature);
    } catch (e) {
      this.log.error(`${e}`);
    }
    try {
      const requiredTemperature = await this.getData(
        this.GetRequiredTemperature
      );
      if (requiredTemperature !== null) {
        this.requiredTemperature = requiredTemperature;
        this.log.debug(
          `updated cached required temperature: ${this.requiredTemperature}`
        );
      }
    } catch (e) {
      this.log.error(`${e}`);
    } finally {
      // Update Characteristics
      if (old_temperature !== this.requiredTemperature) {
        this.thermostatService
          .getCharacteristic(hap.Characteristic.TargetTemperature)
          .updateValue(this.requiredTemperature);
        this.log.debug(
          `updating characteristic value with cached required temperature: ${this.requiredTemperature}`
        );
      }
    }
  }

  // Set Required Temperature
  private async setTargetTemperature(
    value: CharacteristicValue,
    callback: CharacteristicSetCallback
  ): Promise<void> {
    try {
      this.requiredTemperature = value as number;
      try {
        callback(null, this.requiredTemperature);
      } catch (e) {
        this.log.error(`${e}`);
      }
      await this.setData(this.SetRequiredTemperature, this.requiredTemperature);
      this.thermostatService
        .getCharacteristic(hap.Characteristic.TargetTemperature)
        .updateValue(this.requiredTemperature);
      this.log.debug(`Set Target Temperature to ${this.requiredTemperature}`);
    } catch (e) {
      this.log.error(`${e}`);
    }
  }

  // Get Current Temperature
  private async getTemperature(
    callback: CharacteristicGetCallback
  ): Promise<void> {
    const old_temperature = this.temperature;
    try {
      callback(null, this.temperature);
    } catch (e) {
      this.log.error(`${e}`);
    }
    try {
      const temperature = await this.getData(this.GetCurrentTemperature);
      if (temperature !== null) {
        this.temperature = temperature;
        this.log.debug(`updated cached temperature: ${this.temperature}`);
      }
    } catch (e) {
      this.log.error(`${e}`);
    } finally {
      // Update Characteristics
      if (old_temperature !== this.temperature) {
        this.thermostatService
          .getCharacteristic(hap.Characteristic.CurrentTemperature)
          .updateValue(this.temperature);
        this.log.debug(
          `updating characteristic value with cached temperature: ${this.temperature}`
        );
      }
    }
  }

  // Get Display Units
  private getDisplayUnits(callback: CharacteristicGetCallback): void {
    this.log.debug(`Responding with display units: ${this.display_units}`);
    callback(null, this.display_units);
  }

  // Set Display Units
  private setDisplayUnits(
    value: CharacteristicValue,
    callback: CharacteristicSetCallback
  ): void {
    this.display_units = value as number;
    this.log.debug(`Set display units: ${this.display_units}`);
    callback(null, value);
  }

  private async getData(action: string) {
    const json = await axios.post(this.serviceURL, { actions: [action] });
    if (json && json.data.data[action]) {
      return json.data.data[action];
    }
    return null;
  }

  private async setData(action: string, value) {
    await axios.post(this.serviceURL, { actions: [{ [action]: value }] });
  }
}

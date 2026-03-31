# Build various functions for laps completed, stints on all tyre compounds

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec

import fastf1
from fastf1 import utils

from fastf1.utils import delta_time
import fastf1.plotting

'''
Practice
1. No. of Laps completed
2. Stints on all tyre compounds


Qualifying
1. Car setup comparsion
2. Fastest Laps Comparison

Race
1. LapTimes box plot
2. 0-200 acceleration
3. Gap to leader

'''

class Practice():
    def __init__(self,session):
        self.session = session

    def laps_completed(self):
        df = self.session
        
        return df[df['IsAccurate'] == True].groupby(by='Driver').size()
    
    def stints(self):
        fig,ax =plt.subplots(figsize=(25,9))

        df = self.session
        df = df[df['IsAccurate'] == True]

        return sns.violinplot(data=df,x='Driver',y='LapTime',hue='Compound',ax=ax)
    
class Qualifying():
    def __init__(self,session):
        self.session = session
        q1,q2,q3 = self.session.laps.split_qualifying_sessions()
        self.q1 = q1.pick_accurate()
        self.q2 = q2.pick_accurate()
        self.q3 = q3.pick_accurate()

    def compare_laps(self,drivers,save=False):
        laps = []
        
        fig = plt.figure(figsize=(20, 15))
        gs = gridspec.GridSpec(4, 1, height_ratios=[1, 0.75, 0.5, 0.5])  # Define grid with different heights

        ax0 = fig.add_subplot(gs[0])
        ax1 = fig.add_subplot(gs[1])
        ax1.axhline(y=0, color='yellow', linestyle='dotted', linewidth=0.5)
        ax2 = fig.add_subplot(gs[2])
        ax3 = fig.add_subplot(gs[3])

        for i in drivers:
            laps.append([i,self.q3.pick_driver(i).pick_fastest()['LapTime']])
            laps.sort(key=lambda x: x[1])


        for i in drivers:
            data = self.q3.pick_driver(i).pick_fastest().get_telemetry(frequency=20).add_distance()
            
            # Speed Plot            
            ax0.plot(data['Distance'], data['Speed'], label=self.session.get_driver(i)['LastName'], color=fastf1.plotting.get_driver_color(i,session=self.session))
            
            # Gap(Diff) Plot
            if i != laps[0][0]:
                delta_time, ref_tel, compare_tel = utils.delta_time(self.q3.pick_driver(laps[0][0]).pick_fastest(), self.q3.pick_driver(i).pick_fastest())
                ax1.plot(ref_tel['Distance'],delta_time, label=f'{laps[0][0]}-{i} Diff', color=fastf1.plotting.get_driver_color(i,session=self.session),linestyle='dotted')
            
            # Throttle Plot            
            ax2.plot(data['Distance'], data['Throttle'], label=self.session.get_driver(i)['LastName'], color=fastf1.plotting.get_driver_color(i,session=self.session))

            # Brake Plot
            ax3.plot(data['Distance'], data['Brake'], label=self.session.get_driver(i)['LastName'], color=fastf1.plotting.get_driver_color(i,session=self.session))
            
        
        for corner_index in range(len(self.session.get_circuit_info().corners)):
            ax0.axvline(x=self.session.get_circuit_info().corners['Distance'][corner_index], color='yellow', linestyle='--', linewidth=0.5)
            ax0.text(self.session.get_circuit_info().corners['Distance'][corner_index], self.session.laps.pick_fastest().get_telemetry().Speed.min(), f'{corner_index}', ha='center', va='bottom')

            ax1.axvline(x=self.session.get_circuit_info().corners['Distance'][corner_index], color='yellow', linestyle='--', linewidth=0.5)
            ax1.text(self.session.get_circuit_info().corners['Distance'][corner_index], 0, f'{corner_index}', ha='center', va='bottom')
        
            ax2.axvline(x=self.session.get_circuit_info().corners['Distance'][corner_index], color='yellow', linestyle='--', linewidth=0.5)
            ax2.text(self.session.get_circuit_info().corners['Distance'][corner_index], 0, f'{corner_index}', ha='center', va='bottom')

            ax3.axvline(x=self.session.get_circuit_info().corners['Distance'][corner_index], color='yellow', linestyle='--', linewidth=0.5)
            ax3.text(self.session.get_circuit_info().corners['Distance'][corner_index], 0, f'{corner_index}', ha='center', va='bottom')

        ax0.legend(loc='lower right')
        ax0.set_title("Speed")
        
        ax1.legend(loc='lower right')
        ax1.set_title("Gap (Diff)")
            
        ax2.legend(loc='lower right')
        ax2.set_title("Throttle")

        ax3.legend(loc='lower right')
        ax3.set_title("Brake")

        plt.tight_layout()
        plt.show()

        if save:
            plt.savefig(f'{format(self.session.session_info['StartDate'],'%Y')}_{self.session.session_info['Meeting']['Location']}_{self.session.session_info['Type']}_Q3Comparison')

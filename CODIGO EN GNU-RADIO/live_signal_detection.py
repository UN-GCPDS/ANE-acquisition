#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Live Signal Detection
# GNU Radio version: 3.10.7.0

from packaging.version import Version as StrictVersion
from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import blocks, gr
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import gnuradio.inspector as inspector
from gnuradio import qtgui
import sip
import live_signal_detection_python_mod as python_mod  # embedded python module
import osmosdr
import time
import threading



class live_signal_detection(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Live Signal Detection", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Live Signal Detection")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "live_signal_detection")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.thres = thres = -65
        self.samp_rate = samp_rate = 2400000
        self.fun_prob1 = fun_prob1 = 0
        self.fc = fc = 95.7e6

        ##################################################
        # Blocks
        ##################################################

        self._thres_range = Range(-120, 50, 1, -65, 200)
        self._thres_win = RangeWidget(self._thres_range, self.set_thres, "Threshold", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._thres_win)
        self.probSign1 = blocks.probe_signal_f()
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ''
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(fc, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(25, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            10,
            firdes.low_pass(
                1,
                samp_rate,
                25e4,
                10e4,
                window.WIN_HAMMING,
                6.76))
        self.inspector_signal_detector_cvf_0 = inspector.signal_detector_cvf((samp_rate/10), 4096, window.WIN_HAMMING, thres,  0.2, False, 0.2, 0.001, 10000, '')
        self.inspector_qtgui_sink_vf_0 = inspector.qtgui_inspector_sink_vf(
          (samp_rate/10),
          4096,
          fc,
          1,
          1,
          False
        )
        self._inspector_qtgui_sink_vf_0_win = sip.wrapinstance(self.inspector_qtgui_sink_vf_0.pyqwidget(), Qt.QWidget)

        self.top_layout.addWidget(self._inspector_qtgui_sink_vf_0_win)
        def _fun_prob1_probe():
          while True:

            val = self.probSign1.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_fun_prob1,val))
              except AttributeError:
                self.set_fun_prob1(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (10))
        _fun_prob1_thread = threading.Thread(target=_fun_prob1_probe)
        _fun_prob1_thread.daemon = True
        _fun_prob1_thread.start()
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, (samp_rate/10), True, 0 if "auto" == "auto" else max( int(float(0.1) * (samp_rate/10)) if "auto" == "time" else int(0.1), 1) )
        self.blocks_rms_xx_0 = blocks.rms_cf(0.0001)
        self.blocks_message_debug_0 = blocks.message_debug(True, gr.log_levels.info)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.inspector_qtgui_sink_vf_0, 'map_out'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.inspector_signal_detector_cvf_0, 'map_out'), (self.inspector_qtgui_sink_vf_0, 'map_in'))
        self.connect((self.blocks_rms_xx_0, 0), (self.probSign1, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.inspector_signal_detector_cvf_0, 0))
        self.connect((self.inspector_signal_detector_cvf_0, 0), (self.inspector_qtgui_sink_vf_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_rms_xx_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.low_pass_filter_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "live_signal_detection")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_thres(self):
        return self.thres

    def set_thres(self, thres):
        self.thres = thres
        self.inspector_signal_detector_cvf_0.set_threshold(self.thres)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0.set_sample_rate((self.samp_rate/10))
        self.inspector_qtgui_sink_vf_0.set_samp_rate((self.samp_rate/10))
        self.inspector_signal_detector_cvf_0.set_samp_rate((self.samp_rate/10))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 25e4, 10e4, window.WIN_HAMMING, 6.76))
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def get_fun_prob1(self):
        return self.fun_prob1

    def set_fun_prob1(self, fun_prob1):
        self.fun_prob1 = fun_prob1

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.inspector_qtgui_sink_vf_0.set_cfreq(self.fc)
        self.rtlsdr_source_0.set_center_freq(self.fc, 0)




def main(top_block_cls=live_signal_detection, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
